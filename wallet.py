#!/usr/bin/env python3
try :
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    import base64
    import os
    from getpass import getpass
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    from pathlib import Path
    import time
    import sys
    import json
    from colorama import Fore, Style, init

except ModuleNotFoundError:
    print("Modules arent installed yet. run :\npython3 -m pip install --user cryptography argon2-cffi colorama\n On UNIX based OS")

init()

ph = PasswordHasher()

# ~~ Paths ~~

ici = Path(".")
data = Path("data")
mdp = data / "mdp.bin"
authentification = ici / "auth.txt"
salt = ici / "salt.bin"

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

        print(Fore.RED + "/data doesn't exist here. Would you like to create files ?")
        confirm = input("(y/n)").lower()
        print(Style.RESET_ALL)
        if confirm == y:
            data.mkdir()
            mdp.touch()
        else:
            print("Canceled")

    if authentification.exists() and mdp.stat().st_size > 0 and dameow(authentification) == "":
        print(Fore.RED + "Error. Absent master password")
        print(Style.RESET_ALL)
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

        password_hash = ph.hash(password)

        with authentification.open("w") as f:

            f.write(password_hash)
        key = load_key(password)
        encrypt_database({}, key)

        print("Master password created.\n")

    print("Files checked.")
    return True

# ~~ load_keys ~~

def load_key(master_password):

    kdf = Scrypt(

        salt=salty(),

        length=32,
        n=2**14,
        r=8,
        p=1,

    )

    key = kdf.derive(master_password.encode())

    return base64.urlsafe_b64encode(key)

# ~~ Fernet ~~

def encrypt_database(passwords, key):

    fernet = Fernet(key)

    data = json.dumps(passwords)

    cipher = fernet.encrypt(data.encode())

    mdp.write_bytes(cipher)

# ~~ decrypt ~~

def decrypt_database(key):

    if not mdp.exists() or mdp.stat().st_size == 0:
        return {}

    fernet = Fernet(key)

    try:

        cipher = mdp.read_bytes()

        data = fernet.decrypt(cipher)

        return json.loads(data.decode())

    except InvalidToken:

        print(Fore.RED + "FATAL : Unable to decrypt database.")
        print(Style.RESET_ALL)
        return {}

# ~~ hmm salty ~~

def salty():

    if not salt.exists():

        random = os.urandom(16)

        salt.write_bytes(random)

    return salt.read_bytes()

# ~~ password ~~


def entry(THE_PASS):
    count = 3

    while True:
        ePass = getpass("Enter the master password: ")

        try:

            ph.verify(THE_PASS, ePass)

            print(Fore.GREEN + "Correct password.")
            print(Style.RESET_ALL)
            return ePass
        except VerifyMismatchError:

            count -= 1

            print(Fore.RED + "Incorrect password,", count, "attempt(s) left.")
            print(Style.RESET_ALL)
            if count == 0:

                print("Waiting for 1 minute...")
                time.sleep(60)

                print("Done waiting!")

                count = 3
                print("You can try again")

# ~~ list stuff ~~

def list_sites(key):

    passwords = decrypt_database(key)

    print(f"\n{Fore.CYAN}Saved websites:\n{Style.RESET_ALL}")

    for i, site in enumerate(passwords):

        if i % 2 == 0:
            print(f"{Fore.RED} - {site}{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE} - {site}{Style.RESET_ALL}")

# ~~ add password ~~

def add(key):

    passwords = decrypt_database(key)

    site = input("Website: ").lower()
    password = input("Password: ")

    if site in passwords:

        print("A password already exists for", site)

        confirm = input("Replace it? (y/n): ")

        if confirm.lower() != "y":

            print("Canceled.")
            return

    passwords[site] = password

    encrypt_database(passwords, key)

    print("Password saved.")



# ~~ read password ~~

def read(key):

    passwords = decrypt_database(key)

    site = input("Website: ").lower()

    if site in passwords:

        print(passwords[site])

    else:

        print("Password not found.")


# ~~ delete password ~~

def delete(key):

    passwords = decrypt_database(key)

    site = input("Website: ").lower()

    if site in passwords:

        del passwords[site]

        encrypt_database(passwords, key)

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
                    "    -a,  --add        Add or replace a password\n"
                    "    -r,  --read       Display a saved password\n"
                    "    -rp, --reset      Create new master password\n"
                    "    -d,  --delete     Delete a saved password\n"
                    "    -h,  --help       Display this help message\n"
                    "    -l,  --list       Display each existant sites\n"
                    "\n"
                    "EXAMPLES\n"
                    "    wallet -a\n"
                    "    wallet --read\n"
                    "    wallet -d\n"
                    "\n"
                    "Passwords are stored locally.\n"


                    "Made by Soum using Python")
        sys.exit()

try:

    if verification():

        THE_PASS = dameow(authentification)

        if len(sys.argv) < 2:

            print("No argument.")

        else:

            master_password = entry(THE_PASS)

            key = load_key(master_password)

            argument = sys.argv[1]


            if argument == "--add" or argument == "-a":

                add(key)

            elif argument == "--read" or argument == "-r":

                read(key)

            elif argument == "--delete" or argument == "-d":

                delete(key)
            elif argument == "--list" or argument == "-l":

                list_sites(key)
            elif argument == "--reset" or argument == "-rp":

#                reset_password(THE_PASS) 
                 print("Temporally not working :(")
            else:

                print("Unknown argument.")

except KeyboardInterrupt:

    print("\n Fine I'll let ya run away.")


