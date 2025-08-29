import time
import json
import os

from socket import error as SocketError

import requests

from patchedPypresence.presence import Presence, Activity, StatusDisplay
from patchedPypresence.exceptions import PyPresenceException
from utils.logger import setup_logger
from dotenv import load_dotenv


def main():
    try:
        RPC.connect()
    except (PyPresenceException, SocketError) as discord_error:
        LOGGER.error(f"❌ Error while connecting to Discord: {discord_error}")
        reconnect_to_discord()
    except Exception as error:
        LOGGER.error(f"❌ Got an unexpected error: {error}")

    precedent_activity = {}
    precedent_start = 0

    LOGGER.info("🚀 Discord Tidal RPC launched, waiting for Tidal Activity...")

    while True:
        try:
            current_activity = get_tidal_activity()

            if current_activity and current_activity["player"]["status"] == "playing":
                should_update = not (
                    precedent_activity
                    and precedent_activity["title"] == current_activity["title"]
                    and precedent_activity["player"]["status"]
                    == current_activity["player"]["status"]
                    and abs(int(current_activity["currentInSeconds"]) - precedent_start)
                    < 5
                )

                if should_update:
                    to_send = parse_activity(current_activity=current_activity)
                    LOGGER.info(
                        f"Listening to {current_activity['title']} by {current_activity['artists']}"
                    )
                    RPC.update(**to_send)

                precedent_activity = current_activity
                precedent_start = int(current_activity["currentInSeconds"])
            else:
                RPC.clear()
                precedent_activity = {}
                precedent_start = 0

            time.sleep(5 if current_activity else 10)
        except (PyPresenceException, SocketError) as discord_error:
            LOGGER.error(f"❌ Error on discord connection: {discord_error}")
            reconnect_to_discord()
        except Exception as error:
            LOGGER.error(f"❌ Got an unexpected error: {error}")


def reconnect_to_discord():
    """Infinite loop until connected to Discord client"""
    LOGGER.warning("⚠️ Attempting to reconnect to Discord")

    while True:
        try:
            RPC.connect()
            break
        except PyPresenceException as reconnect_error:
            LOGGER.error(f"❌ Failed to reconnect to Discord: {reconnect_error}")
        except SocketError as socker_error:
            if socker_error.errno == 104:
                LOGGER.error(f"❌ Connection reset by peer: {socker_error}")
            else:
                LOGGER.error(
                    f"❌ Got a socket error while connecting to Discord client: {socker_error}"
                )
            LOGGER.warning("⚠️ Retrying in 30 seconds")
            time.sleep(30)
        except Exception as error:
            LOGGER.error(f"❌ Unexpected error while reconnecting to Discord: {error}")
            LOGGER.warning("⚠️ Retrying in 30 seconds")
            time.sleep(30)

    LOGGER.info("✔️ Reconnected successfully to Discord")


def get_tidal_activity() -> dict:
    try:
        r = requests.get(
            f"{os.environ['TIDAL_API_URL']}:{os.environ['TIDAL_API_PORT']}/current",
            headers={"accept": "application/json"},
        )

        return json.loads(r.text)
    except Exception as error:
        LOGGER.error(f"❌ Error while fetching Tidal Hi-Fi API: {error}")
        return {}


def parse_activity(current_activity: dict) -> dict:
    current_time = time.time()
    to_send = dict(state=current_activity["artists"])
    to_send["large_image"] = current_activity["image"]
    to_send["large_text"] = (
        current_activity["album"]
        if current_activity["album"]
        else current_activity["title"]
    )
    to_send["details"] = current_activity["title"]
    to_send["activity_type"] = Activity.LISTENING.value
    to_send["status_display_type"] = StatusDisplay.STATE.value
    to_send["start"] = current_time - current_activity["currentInSeconds"]
    to_send["end"] = current_time + (
        current_activity["durationInSeconds"] - current_activity["currentInSeconds"]
    )

    return to_send


if __name__ == "__main__":
    load_dotenv()
    global LOGGER
    global RPC

    LOGGER = setup_logger(__name__)
    RPC = Presence(os.environ["DISCORD_CLIENT_ID"])
    main()
