# Messaging System User Guide

## Quick Start

### For Patients 👤

1. **Open Messages**
   - Click the "📨 Messages" tab in your dashboard
   - Default view: **Inbox** (messages from clinicians/therapists)

2. **Read Messages**
   - Click any message to view the full conversation
   - Message automatically marks as read when you open it
   - You'll see if your clinician has read your replies

3. **Send a Message**
   - Click "✏️ New Message" subtab
   - Enter recipient username (required)
   - Add subject line (optional)
   - Type your message
   - Click "📤 Send Message"

4. **Check Sent Messages**
   - Click "📤 Sent" subtab
   - See all messages you've sent
   - Green ✓ badge = clinician has read your message
   - Gray ⏳ icon = message not yet read

**Important:** You can send messages to:
- Your assigned therapist ✅
- Other patients ✅
- Developers ✅
- **But NOT to clinicians** ❌ (system will show error)

---

### For Clinicians 👨‍⚕️

1. **Open Clinical Dashboard**
   - After login, you'll see "Clinical Dashboard"
   - Click "📨 Messages" tab

2. **Check Your Inbox**
   - See messages from patients, other clinicians, developers
   - Unread messages highlighted in blue
   - Click to view full conversation

3. **Send Messages to Patients**
   - Click "✏️ New Message" subtab
   - Enter patient username
   - Add subject and message
   - Click "📤 Send Message"

4. **Track Read Status**
   - In "📤 Sent" tab, see which messages patients have read
   - Shows exact time patient read your message
   - Helps you know if important information was received

**You can message:**
- Patients ✅
- Other clinicians ✅
- Therapists ✅
- Developers ✅
- Administrators ✅

---

### For Developers 👨‍💻

1. **Access Developer Dashboard**
   - Click "⚙️ Developer Dashboard" tab
   - You see full system access

2. **Message Colleagues**
   - Click "📨 Messages" subtab
   - Send messages to anyone in the system
   - Track delivery and read status

3. **Review User Feedback**
   - Click "📋 Feedback" subtab (NEW!)
   - See all feedback submissions from all users
   - Shows:
     - Who submitted it (username & role)
     - What category (bug, feature, improvement, etc.)
     - Current status (new, reviewed, in progress, resolved, won't fix)
     - Full feedback text
     - When it was submitted

4. **Filter Feedback**
   - Use dropdown filters to narrow down
   - **By Category:** Bug 🐛, Feature ✨, Improvement 📈, UI 🎨, Performance ⚡, Other 📝
   - **By Status:** New 🆕, Reviewed 👀, In Progress ⚙️, Resolved ✅, Won't Fix ❌
   - Click "Filter" button to apply

---

## Message Features

### Read Receipts
- When someone reads your message, you see a green checkmark (✓)
- Timestamp shows exactly when they opened it
- Helps ensure important communications were received

### Message Search
- (Coming soon) Search across all your conversations
- Find old messages by keyword or date

### Conversation Threading
- Click any message to view the full conversation
- See entire exchange in chronological order
- All replies stay grouped together

### Soft Delete
- Delete messages from your view
- Message stays in database (privacy/audit)
- Other person's copy unaffected

---

## Common Issues & Solutions

### "❌ You cannot send messages to this person"
**Problem:** You tried to send to someone you're not allowed to message  
**Solution:** 
- Patients: Can't message clinicians. Contact them through other means.
- Check recipient username is spelled correctly
- Contact support if username is correct but sending fails

### "⚠️ Recipient not found"
**Problem:** Username doesn't exist or is spelled wrong  
**Solution:**
- Double-check the spelling
- Copy/paste username from user directory if available
- Ask the recipient to confirm their username

### "📭 No messages in your inbox"
**Problem:** No messages yet  
**Solution:**
- Inbox will populate when others send you messages
- Check "📤 Sent" tab to see messages you've sent
- Send a message to start a conversation!

### Message sent but not visible to recipient
**Problem:** They don't see your message  
**Possible causes:**
- They're offline (message will be there when they log in)
- They might have deleted it
- Check the read receipt - if it's unread, they haven't looked yet

---

## Privacy & Security

✅ **All messages are encrypted** at rest in the database  
✅ **Messages are private** between sender and recipient  
✅ **Only YOU can see** your sent/received messages  
✅ **Therapists/Clinicians can only see** conversations with their patients  
✅ **Developers have access** to metadata only for system administration  
✅ **Feedback is anonymized** by default (unless you include identifying info)  

---

## Best Practices

### For Patients
- ✅ Use messages to ask quick questions
- ✅ Keep messages professional and clear
- ✅ Check "Sent" tab to confirm delivery
- ✅ Respond promptly to important messages
- ❌ Don't expect instant responses (check-in times vary)
- ❌ Don't share medical emergencies via message - call 911

### For Clinicians  
- ✅ Review inbox daily
- ✅ Mark as read when reviewed
- ✅ Include subject lines for organization
- ✅ Use messages to check in between appointments
- ❌ Don't rely solely on messages for urgent issues
- ❌ Don't send sensitive info in subject lines

### For Developers
- ✅ Review feedback regularly  
- ✅ Update feedback status as you work on issues
- ✅ Respond to feature requests and bug reports
- ✅ Use feedback to prioritize development work
- ✅ Close feedback when issues are resolved
- ❌ Don't ignore bugs - mark "In Progress" while working

---

## Tips & Tricks

🔍 **Finding Old Messages**
- Sort by date (newest/oldest)
- Use conversation list to jump to specific person
- Read messages stay at top of inbox

🎯 **Quick Message Sending**
- Use Tab key to navigate form fields quickly
- Ctrl+Enter (Windows) or Cmd+Enter (Mac) to send

📌 **Important Messages**
- Can't pin messages, but you can screenshot
- Message will be in "Sent" tab forever (unless deleted)
- Read timestamp shows when recipient saw it

🔔 **Notifications**
- Currently no notifications (email alerts coming soon)
- Check Messages tab regularly to see new messages
- Badge will show when you have unread messages

---

## FAQ

**Q: Can I unsend a message?**  
A: No, but you can delete it from your view. The recipient still has a copy.

**Q: How long are messages kept?**  
A: Indefinitely, unless you manually delete them.

**Q: Can I send files or attachments?**  
A: Not yet. Use shared document links (Google Docs, etc.) if needed.

**Q: What if I accidentally send to the wrong person?**  
A: Delete it from your sent folder. They'll still see it unless they delete it too.

**Q: Can I message someone not in the system?**  
A: No, all recipients must be registered users with valid usernames.

**Q: Will therapists see my messages to developers?**  
A: No. Messages are private between sender and recipient only.

**Q: How do I know if someone is online?**  
A: No online status yet. Messages will be waiting when they log in.

---

## Getting Help

If you encounter issues with messaging:

1. **Check this guide** - Your answer might be here
2. **Contact your clinician/therapist** - For delivery issues
3. **Reach out to developers** - For bugs or feature requests
4. **Submit feedback** - Use the feedback system in the app
5. **Contact support** - Email or in-app support form

---

Last Updated: February 4, 2026  
Messaging System Version: 1.0
