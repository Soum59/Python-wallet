from pathlib import Path
import time
import sys

# ~~ Paths ~~

data = Path("data")
mdp = data / "mdp.txt"

# ~~ verification ~~

def verification():

    if not data.exists():

        print("The 'data' directory doesn't exist. Would you like to create it ?")
        confirm = input("(y/n): ")

        if confirm.lower() == "y":

            data.mkdir()
            mdp.touch()
            print("Files created successfully.")

        else:

            print("Canceled.")
            return False

    elif not mdp.exists():

        mdp.touch()

    print("Files checked.")
    return True

# ~~ password ~~

def entry():

    password = "dddd"

    count = 3

    while True:

        ePass = input("Enter password: ")

        if ePass == password:

            print("Correct password.")
            return True

        count -= 1
        print("Incorrect password,", count, "attempt(s) left.")

        if count == 0:

            print("Waiting for 1 minute...")
            time.sleep(60)
            print("Done waiting!")

            count = 3

# ~~ save passwords ~~

def save_passwords(passwords):

    with mdp.open("w") as f:

        for site, password in passwords.items():

            f.write(f"{site}={password}\n")

# ~~ load passwords ~~

def load_passwords():

    passwords = {}

    with mdp.open("r") as f:

        for ligne in f:

            ligne = ligne.strip()

            if ligne == "":
                continue

            site, password = ligne.split("=")

            passwords[site] = password

    return passwords

# ~~ add password ~~

def add():

    passwords = load_passwords()

    site = input("Website: ")
    password = input("Password: ")

    if site in passwords:

        print("A password already exists for", site)

        confirm = input("Replace it? (y/n): ")

        if confirm.lower() != "y":

            print("Canceled.")
            return

    passwords[site] = password

    save_passwords(passwords)

    print("Password saved.")

# ~~ read password ~~

def read():

    passwords = load_passwords()

    site = input("Website: ")

    if site in passwords:

        print(passwords[site])

    else:

        print("Password not found.")

# ~~ delete password ~~

def delete():

    passwords = load_passwords()

    site = input("Website: ")

    if site in passwords:

        del passwords[site]

        save_passwords(passwords)

        print("Password deleted.")

    else:

        print("Password not found.")

# ~~ arguments ~~

if verification():

    if len(sys.argv) < 2:

        print("No argument.")

    else:

        if entry():

            argument = sys.argv[1]

            if argument == "--add":

                add()

            elif argument == "--read":

                read()

            elif argument == "--delete":

                delete()

            else:

                print("Unknown argument.")
