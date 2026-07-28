from getpass import getpass
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pathlib import Path
import time
import sys

ph = PasswordHasher()

# ~~ Paths ~~

ici = Path(".")
data = Path("data")
mdp = data / "mdp.txt"
authentification = ici / "auth.txt"


# ~~ meow meow ~~

def dameow(authentification):

    with authentification.open("r") as f:
        ligne = f.readline().strip()

    return ligne

# ~~ reset password ~~

def reset_password(THE_PASS):

    print("Reset master password\n")

    old = getpass("Current password: ")

    try:

        ph.verify(THE_PASS, old)

    except VerifyMismatchError:

        print("Wrong password.")
        return

    new = getpass("New password: ")
    confirm = getpass("Confirm password: ")

    if new != confirm:

        print("Passwords don't match.")
        return

    new_hash = ph.hash(new)

    with authentification.open("w") as f:

        f.write(new_hash)

    print("Master password updated.")

# ~~ verification ~~

def verification():

    if not data.exists():

        print("/data doesn't exist. Would you like to create it ?")
        confirm = input("(y/n): ")

        if confirm.lower() == "y":

            data.mkdir()

        else:

            print("Canceled.")
            return False

    if not mdp.exists():

        mdp.touch()

    if mdp.exists() and not authentification.exists():

        print("Authentication file missing.")
        print("Database locked.")
        return False

    if not authentification.exists():

        authentification.touch()

    if dameow(authentification) == "":

        print("No master password detected. Please enter a new one.")

        password = getpass("New password: ")
        confirm = getpass("Confirm password: ")

        if password != confirm:

            print("Passwords don't match.")
            return False

        password = ph.hash(password)

        with authentification.open("w") as f:

            f.write(password)

        print("Master password created.\n")

    print("Files checked.")
    return True

# ~~ password ~~

def entry(THE_PASS):

    count = 3

    while True:

        ePass = getpass("Enter password: ")

        
        try:
            ph.verify(THE_PASS, ePass)
            print("Correct password.")
            return True
        except VerifyMismatchError:
            count -= 1
            print("Incorrect password,", count, "attempt(s) left.")
            if count == 0:
                print("Waiting for 1 minute...")
                time.sleep(60)
                print("Done waiting!")
                count = 3
                print("You can try again")


# ~~ saving stuff ~~

def save_passwords(passwords):

    with mdp.open("w") as f:

        for site, password in passwords.items():

            f.write(f"{site}={password}\n")


# ~~ loading stuff ~~

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

# ~~ list stuff ~~


def list_sites():

    passwords = load_passwords()

    print("\nSaved websites:\n")

    for site in passwords:
        print(" -", site)


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

if len(sys.argv) < 2:
    print("No argument.")
else:
    argument = sys.argv[1]

    if argument == "--help" or argument == "-h":

        print(
                        "Wallet - Local Password Manager\n"
                        "\n"
                        "USAGE\n"
                    "    wallet [OPTION]\n"
                    "\n"
                    "OPTIONS\n"
                    "    -a, --add        Add or replace a password\n"
                    "    -r, --read       Display a saved password\n"
                    "    -d, --delete     Delete a saved password\n"
                    "    -h, --help       Display this help message\n"
                    "\n"
                    "EXAMPLES\n"
                    "    wallet -a\n"
                    "    wallet --read\n"
                    "    wallet -d\n"
                    "\n"
                    "Passwords are stored locally.\n"


                    "Made by Soum using Python")

try:

    if verification():

        THE_PASS = dameow(authentification)

        if len(sys.argv) < 2:

            print("No argument.")

        else:

            if entry(THE_PASS):

                argument = sys.argv[1]

                if argument == "--add" or argument == "-a":

                    add()

                elif argument == "--read" or argument == "-r":

                    read()

                elif argument == "--delete" or argument == "-d":

                    delete()
                
                elif argument == "--list" or argument == "-l":

                    list_sites()
                elif argument == "--reset-password" or argument == "-rp":

                    reset_password(THE_PASS)
                else:

                    print("Unknown argument.")

except KeyboardInterrupt:

    print("\n Fine I'll let ya run away.")
