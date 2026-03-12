import httpx
import os
import datetime
from mcp.server.fastmcp import FastMCP

def register_calendar_tools(mcp: FastMCP):
    api_key = os.getenv("GOOGLE_CALENDAR_API_KEY")
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    @mcp.tool()
    async def calendar_list_events(max_results: int = 10, time_min: str = None) -> str:
        """Lista os próximos eventos da agenda."""
        if not api_key: return "Google Calendar não configurado."
        
        t_min = time_min or datetime.datetime.utcnow().isoformat() + "Z"
        url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
        params = {
            "key": api_key,
            "timeMin": t_min,
            "maxResults": max_results,
            "singleEvents": "true",
            "orderBy": "startTime"
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return f"Erro ao buscar eventos: {resp.text}"
            
            data = resp.json()
            items = data.get("items", [])
            if not items:
                return "Nenhum evento encontrado na agenda."
            
            events = []
            for e in items:
                start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date")
                events.append(f"- {start}: {e.get('summary')} ({e.get('status')})")
            
            return "Eventos agendados:\n" + "\n".join(events)
