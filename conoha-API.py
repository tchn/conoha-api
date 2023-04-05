#!/bin/env python3
import argparse
import requests
import json
from getpass import getpass

menu: list = [
    "0) Show menu", #done
    "1) Show auth token", #done
    "2) Get auth token", #done
    "3) Get server list", #done
    "4) Download custom ISO image", #done
    "5) List downloaded ISO image", #done
    "6) Mount ISO image", #done
    "7) Unmount ISO image", #done
    "x) Exit",
]

auth_data: dict = {
    "auth_token": "",
    "tenant_id": "",
    "servers": [],
    "iso-images": [],
}

def pretty_print_dict(data: dict) -> None:
    print(json.dumps(data, indent=4, sort_keys=True))

def show_menu() -> None:
    list(map( lambda x: print(x), menu ))

def show_auth_token(auth_data: dict) -> None:
    pretty_print_dict(auth_data)

def get_auth_token(main_args, auth_data: dict) -> dict:
    # ToDo
    # Save endpoints URL from serviceCatalog for future use.
    endpoint: str
    username: str
    password: str
    req_data: dict
    endpoint = "https://identity.tyo1.conoha.io/v2.0/tokens"

    if main_args.username is None:
        username: str = input("Username: ")
    else:
        username: str = main_args.username
    if main_args.password is None:
        password: str = getpass("Password: ")
    else:
        password: str = main_args.password
    req_data = {
        "auth": {
            "passwordCredentials": dict(username=username, password=password),
            "tenantId": auth_data["tenant_id"],
        }
    }
    # Using json param automatically set Accept header to application/json
    res_data = requests.post(endpoint, json=req_data)
    if str(res_data.status_code) == "200":
        res_json: dict = res_data.json()
        auth_data["auth_token"] = res_json["access"]["token"]["id"]
    else:
        raise
    return auth_data

def get_server_list(auth_data: dict) -> dict:
    # https://www.conoha.jp/docs/compute-get_vms_list.php
    endpoint: str
    http_headers: dict = {
        "Accept": "application/json",
        "X-Auth-Token": auth_data["auth_token"]
    }
    res_json: dict
    endpoint = f"https://compute.tyo1.conoha.io/v2/%s/servers"
    endpoint = endpoint % auth_data["tenant_id"]

    res_data = requests.get(endpoint, headers=http_headers)
    if str(res_data.status_code) == "200":
        res_json = res_data.json()
        auth_data["servers"] = res_json["servers"]
    else:
        raise
    pretty_print_dict(auth_data["servers"])
    return auth_data

def get_custom_iso_image(main_args, auth_data: dict) -> dict:
    # https://www.conoha.jp/docs/compute-iso-download-add.php
    endpoint: str
    iso_url: str
    http_headers: dict = {
        "Accept": "application/json",
        "X-Auth-Token": auth_data["auth_token"]
    }
    endpoint = f"https://compute.tyo1.conoha.io/v2/%s/iso-images"
    endpoint = endpoint % auth_data["tenant_id"]
    req_data: dict = {"iso-image": ""}

    if main_args.customisourl is None:
        iso_url = input("Enter URL of custom ISO image: ")
    else:
        iso_url = main_args.customisourl
    req_data["iso-image"] = dict(url=iso_url)
    res_data = requests.post(endpoint, headers=http_headers, json=req_data)
    if str(res_data.status_code) == "201":
        return
    else:
        raise

def list_custom_iso_image(auth_data: dict) -> None:
    # WIP
    # https://www.conoha.jp/docs/compute-iso-list-show.php
    endpoint: str
    http_headers: dict = {
        "Accept": "application/json",
        "X-Auth-Token": auth_data["auth_token"]
    }
    res_json: dict
    endpoint = f"https://compute.tyo1.conoha.io/v2/%s/iso-images"
    endpoint = endpoint % auth_data["tenant_id"]

    res_data = requests.get(endpoint, headers=http_headers)
    if str(res_data.status_code) == "200":
        res_json = res_data.json()
        auth_data["iso-images"] = res_json["iso-images"]
    pretty_print_dict(auth_data["iso-images"])
    return auth_data

def mount_iso(auth_data: dict) -> None:
    # WIP
    # https://www.conoha.jp/docs/compute-insert_iso_image.php
    endpoint: str
    server_id: str
    server_name: str
    iso_path: str
    iso_name: str
    idx: int
    http_headers: dict = {
        "Accept": "application/json",
        "X-Auth-Token": auth_data["auth_token"]
    }
    req_data: dict = {"mountImage": ""}
    endpoint = f"https://compute.tyo1.conoha.io/v2/%s/servers/%s/action"

    print("Select server to mount iso image onto:")
    for i in enumerate(auth_data["servers"]):
        print(f"(%d) %s" % (i[0], i[1]["name"]))
    while True:
        idx = int(input("Input number in parenthesis: ") )
        try:
            server_id = auth_data["servers"][idx]["id"]
            server_name = auth_data["servers"][idx]["name"]
        except:
            pass
        finally:
            break
    print(f"Selected server name %s: id %s" % (server_name, server_id))
    endpoint = endpoint % (auth_data["tenant_id"], server_id)

    print("Select iso image to mount:")
    for i in enumerate(auth_data["iso-images"]):
        print(f"(%d) %s" % (i[0], i[1]["name"]))
    while True:
        idx = int(input("Input number in parenthesis: ") )
        try:
            iso_path = auth_data["iso-images"][idx]["path"]
            iso_name = auth_data["iso-images"][idx]["name"]
            print(f"Selected iso name %s: path %s" % (iso_name, iso_path))
            req_data["mountImage"] = iso_path + iso_name
            res_data = requests.post(endpoint, headers=http_headers, json=req_data)
            if res_data == "204":
                return
            else:
                raise
        except UnboundLocalError as error:
            print(error)
        finally:
            break

def unmount_iso(auth_data: dict) -> None:
    # WIP
    # https://www.conoha.jp/docs/compute-eject_iso_image.php
    endpoint: str
    tenant_id: str
    server_id: str
    http_headers: dict = {
        "Accept": "application/json",
        "X-Auth-Token": auth_data["auth_token"]
    }
    req_data: dict = {"unmountImage": ""}
    endpoint = f"https://compute.tyo1.conoha.io/v2/%s/servers/%s/action"

    print("Select server to mount iso image onto:")
    for i in enumerate(auth_data["servers"]):
        print(f"(%d) %s" % (i[0], i[1]["name"]))
    while True:
        idx = int(input("Input number in parenthesis: ") )
        try:
            server_id = auth_data["servers"][idx]["id"]
            server_name = auth_data["servers"][idx]["name"]
        except:
            pass
        finally:
            break
    print(f"Selected server name %s: id %s" % (server_name, server_id))
    endpoint = endpoint % (auth_data["tenant_id"], server_id)
    res_data = requests.post(endpoint, headers=http_headers, json=req_data)
    if str(res_data.status_code) == "204":
        return
    else:
        raise

def main(args: argparse.ArgumentParser, auth_data: dict) -> None:
    if args.token != "":
        auth_data["auth_token"] = args.token
    if args.tenantid != "":
        auth_data["tenant_id"] = args.tenantid
    else:
        auth_data["tenant_id"] = input("TenantID: ")
    while True:
        show_menu()
        selected_menu = input("Select menu : ")
        if selected_menu == "0":
            show_menu()
        elif selected_menu == "1":
            show_auth_token(auth_data)
        elif selected_menu == "2":
            auth_data = get_auth_token(args, auth_data)
        elif selected_menu == "3":
            if auth_data["auth_token"] == "":
                auth_data = get_auth_token(auth_data)
            auth_data = get_server_list(auth_data)
        elif selected_menu == "4":
            if auth_data["auth_token"] == "":
                auth_data = get_auth_token(auth_data)
            get_custom_iso_image(args, auth_data)
        elif selected_menu == "5":
            if auth_data["auth_token"] == "":
                auth_data = get_auth_token(auth_data)
            list_custom_iso_image(auth_data)
        elif selected_menu == "6":
            if auth_data["auth_token"] == "":
                auth_data = get_auth_token(auth_data)
            if len(auth_data["servers"]) == 0:
                auth_data = get_server_list(auth_data)
            if len(auth_data["iso-images"]) == 0:
                auth_data = list_custom_iso_image(auth_data)
            mount_iso(auth_data)
        elif selected_menu == "7":
            if len(auth_data["auth_token"]) == 0:
                auth_data = get_auth_token(auth_data)
            if len(auth_data["servers"]) == 0:
                auth_data = get_server_list(auth_data)
            unmount_iso(auth_data)
        elif selected_menu == "x":
            exit()

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--token", type=str, help="Auth Token")
    arg_parser.add_argument("--tenantid", type=str, help="Tenant ID")
    arg_parser.add_argument("--username", type=str, help="Username")
    arg_parser.add_argument("--password", type=str, help="Password")
    arg_parser.add_argument("--customisourl", type=str, help="Custom ISO URL")
    args = arg_parser.parse_args()
    main(args, auth_data)