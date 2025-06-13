
# Bot To organize party with friend
This bot automatically organizes events based on a template category that it copies. It is currently not universal, and several variables need to be modified directly in the code. There is also an issue with the virtual environment (venv), which strangely doesn't contain the pre-installed modules. As a result, it needs to be recreated from scratch each time.

## Installation 🏗️
```bash
python3 -m venv bot_env
source bot_env/bin/activate.
pip install discord.py python-dotenv
```
Use ```deactivate``` to go out of the env.

## Utilisation
Currently, you need to use '!' before a command to execute it.

## Function available

### clear_channel
As its name suggests, this function clears the channel it is in.  
Utilisation: ```!clear_channel```

### delete_category
Deletes the specified category and all of its channels.  
⚠️ This operation is permanent.  
Note: This function do weird stuff when the category's name contain some space  
Utilisation: ```!delete_category "category's name"```

### create_party
It creates a category from the template specified in the code (via its ID), copying all included channels and permissions.
Note: This function currently lacks proper safeguards, and some features were intentionally left out for simplicity. Further updates are expected.  
Utilisation: ```!create_party "party's name" "party's description"```
