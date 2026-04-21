### sample format of webhook


✅ ## 1. Resistance Hold (you already have)
{
  "message": "Res_Hold Time=2026-04-19 10:30 Price=78477 Type=buyPE"
}
✅ ## 2. Support Hold
{
  "message": "Sup_Hold Time=2026-04-19 10:30 Price=78400 Type=buyCE"
}
✅ ## 3. Resistance → Support (Breakout)
{
  "message": "Res_to_Sup Time=2026-04-19 10:30 Price=78450 Type=buyCE"
}
✅ ## 4. Support → Resistance (Breakdown)
{
  "message": "Sup_to_Res Time=2026-04-19 10:30 Price=78500 Type=buyPE"
}