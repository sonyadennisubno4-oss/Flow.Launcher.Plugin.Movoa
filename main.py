#!/usr/bin/env python3
"""Flow Launcher plugin for Movoa AI Video Generator (https://movoa.ai/).

Unlimited AI video generator with sound: on paid plans the tenth take of a shot
costs what the first did, and your first clip is free to make right now.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

SITE_URL = "https://movoa.ai"


def api_post(path, api_key, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{SITE_URL}{path}",
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.strip()}",
            "User-Agent": "Flow.Launcher.Plugin.Movoa/1.0.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def handle_query(query):
    text = (query or "").strip()
    if not text:
        return [
            {
                "Title": "Movoa AI Video Generator",
                "SubTitle": "Type a prompt to generate an AI video clip with sound, or press Enter to open movoa.ai",
                "IcoPath": "icon.png",
                "JsonRPCAction": {"method": "open_url", "parameters": [SITE_URL]},
            }
        ]
    api_key = os.environ.get("MOVOA_API_KEY", "").strip()
    results = [
        {
            "Title": f"Open in Movoa: {text[:60]}",
            "SubTitle": "Create a video clip with synchronized sound on movoa.ai",
            "IcoPath": "icon.png",
            "JsonRPCAction": {
                "method": "open_url",
                "parameters": [f"{SITE_URL}/video/text-to-video?prompt={urllib.parse.quote(text)}"],
            },
        }
    ]
    if api_key:
        results.insert(
            0,
            {
                "Title": f"Submit via Movoa API: {text[:55]}",
                "SubTitle": "Queue a MiniMax H3 6s video clip with sound using MOVOA_API_KEY",
                "IcoPath": "icon.png",
                "JsonRPCAction": {"method": "submit_video", "parameters": [text]},
            },
        )
    return results


def handle_method(method, params):
    if method == "open_url" and params:
        webbrowser.open(str(params[0]))
        return
    if method == "submit_video" and params:
        api_key = os.environ.get("MOVOA_API_KEY", "").strip()
        if not api_key:
            webbrowser.open(f"{SITE_URL}/settings/apikeys")
            return
        try:
            api_post(
                "/api/ai/generate",
                api_key,
                {
                    "provider": "auto",
                    "mediaType": "video",
                    "model": "minimax-h3",
                    "scene": "text-to-video",
                    "prompt": str(params[0]),
                    "options": {"duration": 6, "resolution": "480p", "aspect_ratio": "16:9", "sound": True},
                },
            )
        except Exception:
            pass
        webbrowser.open(f"{SITE_URL}/video/text-to-video")


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"result": handle_query("")}))
        return
    req = json.loads(sys.argv[1])
    method = req.get("method", "query")
    params = req.get("parameters", [])
    if method == "query":
        q = params[0] if params else ""
        print(json.dumps({"result": handle_query(q)}))
    else:
        handle_method(method, params)


if __name__ == "__main__":
    main()
