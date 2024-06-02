import streamlit as st
from tinydb import TinyDB, Query
import pandas as pd
import os

# Database setup
DB_PATH = "dnd_users.json"
db = TinyDB(DB_PATH)
User = Query()

# Predefined list of weapons
dnd_5e_weapons = [
    "Club",
    "Dagger",
    "Greatclub",
    "Handaxe",
    "Javelin",
    "Light Hammer",
    "Mace",
    "Quarterstaff",
    "Sickle",
    "Spear",
    "Light Crossbow",
    "Dart",
    "Shortbow",
    "Sling",
    "Battleaxe",
    "Flail",
    "Glaive",
    "Greataxe",
    "Greatsword",
    "Halberd",
    "Lance",
    "Longsword",
    "Maul",
    "Morningstar",
    "Pike",
    "Rapier",
    "Scimitar",
    "Shortsword",
    "Trident",
    "War Pick",
    "Warhammer",
    "Whip",
    "Blowgun",
    "Hand Crossbow",
    "Heavy Crossbow",
    "Longbow",
    "Net"
]

#Function to sort out xp levels, and automatically upgrade the character
def xp_to_level(level, xp):
        xpDict = {1:300,
                  2:900,
                  3:2700,
                  4:6500,
                  5:14000,
                  6:23000,
                  7:34000,
                  8:48000,
                  9:64000,
                  10:85000,
                  11:100000,
                  12:120000,
                  13:140000,
                  14:165000,
                  15:195000,
                  16:225000,
                  17:265000,
                  18:305000,
                  19:355000}
        xpTotal = xp
        levelTotal = level
        if levelTotal in xpDict.keys():
            xpNecessary = xpDict.setdefault(levelTotal)
            if xpTotal > xpNecessary:
                while xpTotal > xpNecessary:
                    levelTotal += 1
                    xpTotal -= int(xpNecessary)
                    #print("The xp total is: ", xpTotal)
                    xpNecessary = xpDict.setdefault(levelTotal)
                    #print("Your current level is: ", levelTotal)
                return (xpTotal, levelTotal)
            else:
                return (xpTotal, levelTotal)


# Function to load data from TinyDB
def load_data():
    users = db.all()
    if not users:
        return pd.DataFrame(columns=['ID', 'name', 'xp', 'level', 'weapons'])
    else:
        for user in users:
            user['ID'] = user.doc_id
        return pd.DataFrame(users)

# Function to insert a new user
def insert_user(name, xp, level, weapons):
    if db.search(User.name == name):
        st.error("User with this name already exists.")
    else:
        new_user = {'name': name, 'xp': xp, 'level': level, 'weapons': weapons}
        db.insert(new_user)
        st.experimental_rerun()  # Refresh the page after insertion

# Function to update a user
def update_user(user_id, name, xp, level, weapons):
    db.update({'name': name, 'xp': xp, 'level': level, 'weapons': weapons}, doc_ids=[user_id])
    st.experimental_rerun()  # Refresh the page after update

# Function to delete a user
def delete_user(user_id):
    db.remove(doc_ids=[user_id])
    st.experimental_rerun()  # Refresh the page after deletion

# Load the data
df = load_data()

# Streamlit app
st.title("D&D User Management App")

# Select user to update or add a new user
st.header("Add or Update User")
user_names = ["New User"] + list(df['name']) if not df.empty else ["New User"]
selected_user_name = st.selectbox("Select User", user_names)

if selected_user_name != "New User":
    user = df[df['name'] == selected_user_name].iloc[0]
    name = st.text_input("Name", user['name'])
    xp = st.number_input("XP", min_value=0, value=user['xp'])
    level = st.number_input("Level", min_value=0, value=user['level'])
    weapons = st.multiselect("Weapons", dnd_5e_weapons, default=user['weapons'])
    user_id = user['ID']
else:
    name = st.text_input("Name")
    xp = st.number_input("XP", min_value=0)
    level = st.number_input("Level", min_value=0)
    weapons = st.multiselect("Weapons", dnd_5e_weapons)
    user_id = None

if st.button("Submit"):
    if user_id is None:
        if name:
            newXp, newLevel = xp_to_level(level, xp)

            insert_user(name, newXp, newLevel, weapons)
        else:
            st.error("Please provide a name.")
    else:
        if name:
            update_user(user_id, name, xp, level, weapons)
else:
    st.write("Select a user to update or enter details for a new user.")

# Delete user
st.header("Delete User")
delete_user_name = st.selectbox("Select User to Delete", user_names[1:], key="delete_user")
if st.button("Delete Selected User"):
    if delete_user_name:
        user_id_delete = df[df['name'] == delete_user_name].iloc[0]['ID']
        delete_user(user_id_delete)
    else:
        st.error("Please provide user name.")

# Display the updated user table only once
st.header("Updated User Table")
df['weapons'] = df['weapons'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
st.dataframe(df)
