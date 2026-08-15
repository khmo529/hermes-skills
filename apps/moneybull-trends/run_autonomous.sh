#!/bin/bash
set -euo pipefail
BASE=/home/hogh0608/htdocs/moneybull.co.kr/current-trends
LOG=/home/hogh0608/htdocs/moneybull.co.kr/current-trends/evolution.log
TRENDS_JSON=/home/hogh0608/htdocs/moneybull.co.kr/wp-content/uploads/moneybull/trends.json
echo "[$(date)] autonomous agent bootstrap" >> "$LOG"
# kill previous agent if any
pkill -f "python3 $BASE/autonomous_agent.py" || true
# run agent in background
cd "$BASE"
nohup python3 "$BASE/autonomous_agent.py" >> "$LOG" 2>&1 &
echo "PID: $!"
echo "로그: tail -f $LOG"
# 1-minute cron fallback: refresh trends.json every minute
(crontab -l 2>/dev/null | grep -v "current-trends/fetcher.py" || true
printf '%s\n' "* * * * * cd $BASE && python3 fetcher.py > $TRENDS_JSON 2>/dev/null; chown www-data:www-data $TRENDS_JSON 2>/dev/null") | crontab -
