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

    if not authentification.exists():

        authentification.touch()

    if dameow(authentification) == "":

        print("No master password detected. Please enter a new one.")

        password = input("New password: ")
        confirm = input("Confirm password: ")

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

        ePass = input("Enter password: ")

        
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


# ~~ loading shit ~~

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

try:

    if verification():

        THE_PASS = dameow(authentification)

        if len(sys.argv) < 2:

            print("No argument.")

        else:

            if entry(THE_PASS):

                argument = sys.argv[1]

                if argument == "--add":

                    add()

                elif argument == "--read":

                    read()

                elif argument == "--delete":

                    delete()

                else:

                    print("Unknown argument.")

except KeyboardInterrupt:

    print("\n Fine I'll let ya run away.")
