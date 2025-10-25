# CalibreMCP User Prompt Template

## What should I read next?

Analyze my Calibre library collection, reading history, and current series progress to provide personalized reading recommendations. Use Austrian efficiency to eliminate decision paralysis - give me specific book suggestions with priority rankings and tell me exactly which book I should read right now.

### Context to Consider:
- **Current Library**: {{library_name}} ({{book_count}} books)
- **Active Series**: {{active_series}}
- **Recent Reads**: {{recent_books}}
- **Preferred Genres**: {{preferred_genres}}
- **Reading Goals**: {{reading_goals}}

### What I Need:
1. **Top 3 Recommendations** with specific reasoning
2. **Series Continuation** - which series should I continue?
3. **New Discoveries** - books I haven't read that match my interests
4. **Priority Ranking** - what should I read RIGHT NOW?

### Response Format:
```
🎯 IMMEDIATE RECOMMENDATION: [Book Title] by [Author]
📚 WHY: [Specific reasoning based on my preferences]
📖 SERIES: [Series info if applicable]

📋 TOP 3 RECOMMENDATIONS:
1. [Book] - [Reason]
2. [Book] - [Reason]  
3. [Book] - [Reason]

🔄 CONTINUE SERIES:
- [Series Name]: [Next Book] (Book X of Y)

🆕 NEW DISCOVERIES:
- [Book] - [Why it matches my interests]
```

Use my library data to make intelligent, personalized recommendations that eliminate decision paralysis and get me reading immediately.
