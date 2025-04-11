from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from datetime import datetime
import pytz
import asyncpg
import os
import logging
# import dateparser # Removed due to dependency conflict
# from dateparser.search import search_dates # Removed due to dependency conflict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection details (ideally from environment variables)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/database")

async def get_db_connection():
    """Establishes an async database connection."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Database connection established.")
        # Ensure the table exists
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                task TEXT NOT NULL,
                reminder_time TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

async def close_db_connection(conn):
    """Closes the database connection."""
    if conn:
        await conn.close()
        logger.info("Database connection closed.")

# --- Time Zone and Date Parsing Utilities ---

# Commented out due to dateparser removal
# def parse_datetime_with_timezone(date_str: str, time_str: str, tz_str: str) -> Union[datetime, None]:
#     """Parses date and time strings into a timezone-aware datetime object."""
#     try:
#         # Combine date and time for parsing
#         full_datetime_str = f"{date_str} {time_str}"
#
#         # Use dateparser which can handle relative dates like "tomorrow" and times like "9am"
#         # Important: Provide the timezone context for correct parsing
#         settings = {'TIMEZONE': tz_str, 'RETURN_AS_TIMEZONE_AWARE': True}
#         parsed_dt = dateparser.parse(full_datetime_str, settings=settings)
#
#         if parsed_dt:
#             logger.info(f"Parsed '{full_datetime_str}' in tz '{tz_str}' as: {parsed_dt}")
#             return parsed_dt
#         else:
#             logger.warning(f"Could not parse datetime string: {full_datetime_str} with timezone {tz_str}")
#             return None
#
#     except Exception as e:
#         logger.error(f"Error parsing datetime '{full_datetime_str}' with timezone '{tz_str}': {e}")
#         return None

def convert_to_utc(dt_aware: datetime) -> Union[datetime, None]:
    """Converts a timezone-aware datetime object to UTC."""
    if not dt_aware or not dt_aware.tzinfo:
        logger.error("Cannot convert naive datetime to UTC. Timezone info missing.")
        return None
    try:
        return dt_aware.astimezone(pytz.utc)
    except Exception as e:
        logger.error(f"Error converting datetime {dt_aware} to UTC: {e}")
        return None

def convert_from_utc(dt_utc: datetime, target_tz_str: str) -> Union[datetime, None]:
    """Converts a UTC datetime object to a target timezone."""
    if not dt_utc or not dt_utc.tzinfo:
        # Assume UTC if naive, though ideally it should always be aware
        dt_utc = pytz.utc.localize(dt_utc) if not dt_utc.tzinfo else dt_utc
    
    try:
        target_tz = pytz.timezone(target_tz_str)
        return dt_utc.astimezone(target_tz)
    except pytz.exceptions.UnknownTimeZoneError:
        logger.error(f"Unknown target timezone: {target_tz_str}")
        return None # Fallback or error needed
    except Exception as e:
        logger.error(f"Error converting UTC datetime {dt_utc} to {target_tz_str}: {e}")
        return None

# --- End Utilities ---

class ValidateReminderForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reminder_form"

    def validate_task(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if len(slot_value) < 3:
            dispatcher.utter_message(text="Please provide a more descriptive task.")
            return {"task": None}
        return {"task": slot_value}

    def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            # Here you would add date parsing logic
            # For now, we'll just accept any value
            return {"date": slot_value}
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid date.")
            return {"date": None}

    def validate_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            # Here you would add time parsing logic
            # For now, we'll just accept any value
            return {"time": slot_value}
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid time.")
            return {"time": None}

    def validate_time_zone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        # Try to normalize common abbreviations or validate using pytz
        try:
            # Check if it's a known timezone
            pytz.timezone(slot_value)
            logger.info(f"Validated timezone: {slot_value}")
            return {"time_zone": slot_value}
        except pytz.exceptions.UnknownTimeZoneError:
             # Add potential mapping for common TZs if needed, or re-prompt
            dispatcher.utter_message(text=f"Sorry, '{slot_value}' is not a recognized timezone. Please use standard names like UTC, EST, PST, Europe/London.")
            return {"time_zone": None}
        except Exception as e:
            logger.error(f"Error validating timezone {slot_value}: {e}")
            dispatcher.utter_message(text="There was an issue validating the timezone.")
            return {"time_zone": None}

class ActionSetReminder(Action):
    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        task = tracker.get_slot("task")
        date_str = tracker.get_slot("date")
        time_str = tracker.get_slot("time")
        time_zone_str = tracker.get_slot("time_zone") or "UTC" # Default to UTC if not provided
        user_id = tracker.sender_id

        # --- Temporarily disabled due to dateparser removal ---
        logger.error("ActionSetReminder attempted, but dateparser functionality is disabled due to dependency conflicts.")
        dispatcher.utter_message(text="Sorry, setting reminders with specific dates/times is temporarily disabled. Please try again later.")
        return [SlotSet("reminder_confirmed", False), SlotSet("task", None), SlotSet("date", None), SlotSet("time", None), SlotSet("time_zone", None)] # Reset slots
        # --- End temporary disable ---

        # Original code using dateparser (commented out):
        # Use the new parsing utility
        # reminder_dt_local = parse_datetime_with_timezone(date_str, time_str, time_zone_str)
        #
        # if not reminder_dt_local:
        #     dispatcher.utter_message(text=f"Sorry, I couldn't understand the date '{date_str}' and time '{time_str}'. Please try again.")
        #     # Potentially re-trigger form or specific slot validation
        #     return [] # Or trigger re-validation
        #
        # # Convert to UTC for storage
        # reminder_dt_utc = convert_to_utc(reminder_dt_local)
        # if not reminder_dt_utc:
        #      dispatcher.utter_message(text="Sorry, there was an error processing the time zone.")
        #      return []
        #
        # conn = await get_db_connection()
        # if not conn:
        #     dispatcher.utter_message(text="Sorry, I couldn't connect to the database to save your reminder.")
        #     return []
        #
        # try:
        #     # Insert UTC time into database
        #     reminder_id = await conn.fetchval(
        #         "INSERT INTO reminders (user_id, task, reminder_time) VALUES ($1, $2, $3) RETURNING id",
        #         user_id, task, reminder_dt_utc # Store UTC time
        #     )
        #     logger.info(f"Reminder {reminder_id} saved for user {user_id} at {reminder_dt_utc} (UTC).")
        #
        #     # Confirm using the user's original input strings and timezone
        #     dispatcher.utter_message(
        #         response="utter_confirm_reminder",
        #         task=task,
        #         date=date_str,
        #         time=time_str,
        #         time_zone=time_zone_str
        #     )
        #     # Optionally store the user's preferred timezone if it wasn't just provided
        #     # This part would ideally go into a user profile action/update
        #     # events.append(SlotSet("user_preferred_timezone", time_zone_str))
        #     return [SlotSet("reminder_confirmed", True), SlotSet("last_reminder_id", str(reminder_id))]
        #
        # except Exception as e:
        #     logger.error(f"Failed to save reminder: {e}")
        #     dispatcher.utter_message(text="Sorry, I encountered an error while saving your reminder.")
        #     return []
        # finally:
        #     await close_db_connection(conn)

class ActionListReminders(Action):
    def name(self) -> Text:
        return "action_list_reminders"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        user_id = tracker.sender_id
        # Attempt to get user's preferred timezone (needs proper storage mechanism)
        # For now, default to UTC or last provided timezone if available
        user_pref_tz = tracker.get_slot("time_zone") or "UTC"
        conn = await get_db_connection()

        if not conn:
            dispatcher.utter_message(text="Sorry, I couldn't connect to the database to retrieve your reminders.")
            return []

        try:
            reminders_utc = await conn.fetch(
                "SELECT id, task, reminder_time FROM reminders WHERE user_id = $1 ORDER BY reminder_time ASC",
                user_id
            )

            if not reminders_utc:
                dispatcher.utter_message(response="utter_no_reminders")
            else:
                reminder_list_parts = []
                for r in reminders_utc:
                    reminder_dt_utc = r['reminder_time']
                    # Convert UTC time from DB to user's preferred timezone for display
                    reminder_dt_local = convert_from_utc(reminder_dt_utc, user_pref_tz)
                    if reminder_dt_local:
                        time_str_local = reminder_dt_local.strftime('%Y-%m-%d %H:%M %Z')
                    else:
                        # Fallback to UTC display if conversion fails
                        time_str_local = reminder_dt_utc.strftime('%Y-%m-%d %H:%M UTC') + " (conversion error)"
                    
                    reminder_list_parts.append(
                        f"- ID: {r['id']}, Task: {r['task']}, Time: {time_str_local}"
                    )
                
                reminder_list_str = "\n".join(reminder_list_parts)
                dispatcher.utter_message(response="utter_list_reminders", reminders=reminder_list_str)

            return []

        except Exception as e:
            logger.error(f"Failed to list reminders: {e}")
            dispatcher.utter_message(text="Sorry, I encountered an error while retrieving your reminders.")
            return []
        finally:
            await close_db_connection(conn)

class ActionDeleteReminder(Action):
    def name(self) -> Text:
        return "action_delete_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        reminder_id_to_delete = tracker.get_slot("reminder_id")
        user_id = tracker.sender_id

        if not reminder_id_to_delete:
            # This should ideally be handled by asking the user for the ID
            # or clarifying which reminder if multiple are listed.
            dispatcher.utter_message(text="I need the ID of the reminder you want to delete.")
            # Potentially trigger a clarification flow or re-ask
            return []

        conn = await get_db_connection()
        if not conn:
            dispatcher.utter_message(text="Sorry, I couldn't connect to the database to delete the reminder.")
            return []

        try:
            # Try to convert reminder_id to integer for DB query
            try:
                reminder_id_int = int(reminder_id_to_delete)
            except ValueError:
                logger.warning(f"Invalid reminder ID format provided: {reminder_id_to_delete}")
                dispatcher.utter_message(response="utter_reminder_not_found")
                return [SlotSet("reminder_id", None)] # Clear the slot

            # Execute the delete operation
            result = await conn.execute(
                "DELETE FROM reminders WHERE id = $1 AND user_id = $2",
                reminder_id_int, user_id
            )

            # Check if any row was deleted (result format is 'DELETE N')
            if result == "DELETE 1":
                logger.info(f"Reminder {reminder_id_int} deleted for user {user_id}.")
                dispatcher.utter_message(response="utter_reminder_deleted")
            else:
                logger.warning(f"Reminder {reminder_id_int} not found for user {user_id} or already deleted.")
                dispatcher.utter_message(response="utter_reminder_not_found")

            return [SlotSet("reminder_id", None)] # Clear the slot after attempting deletion

        except Exception as e:
            logger.error(f"Failed to delete reminder {reminder_id_to_delete}: {e}")
            dispatcher.utter_message(text="Sorry, I encountered an error while deleting the reminder.")
            return [SlotSet("reminder_id", None)] # Clear slot on error too
        finally:
            await close_db_connection(conn) 