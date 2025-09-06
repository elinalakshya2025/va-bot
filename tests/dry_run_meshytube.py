#!/usr/bin/env python3
import os, json, sys, time
from connector import MeshyYouTubeConnector  # update import to your connector class


def main():
    try:
        c = MeshyYouTubeConnector(
            meshy_api_key=os.getenv("MESHY_API_KEY"),
            youtube_client_id=os.getenv("YOUTUBE_CLIENT_ID"),
            youtube_client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
            token_store=os.getenv("TOKEN_STORE", "tmp/tokens.json"))
        ok_meshy = c.auth_meshy()
        ok_yt = c.auth_youtube()
        print("Meshy auth:", ok_meshy)
        print("YouTube auth:", ok_yt)

        # heartbeat / basic endpoints
        mesh_status = c.meshy_status()  # returns basic account info
        yt_status = c.youtube_channel_info()  # returns channel id/name
        print(
            json.dumps({
                "meshy": mesh_status,
                "youtube": yt_status
            }, indent=2))
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
