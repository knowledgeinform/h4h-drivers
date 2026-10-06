# Installing a Tak Server via CloudRF's Github Repo

Warning: This current setup of the TAK setup is very fragile. Restarting the docker containers at any point will break it (including restarting the computer).

## Hardware + OS

x86 Processor with Ubuntu 24.04

## Installation Steps

- Install Docker
    - You must add Docker to sudo so that the `docker` command can be run without sudo
    - Normally after following the instructions to do this, you need to restart your computer
- Download a TAK Server Release from `tak.gov/products/tak-server`
    - You will need a TAK account
    - Alternatively, contact `chui1` (who has a TAK account)
- Clone the CloudRF repo
    - `git clone https://github.com/Cloud-RF/tak-server.git`
    - DO NOT rename the `tak-server` folder, that name is hardcoded into the setup script
- Checkout the last known working commit hash
    - `git checkout 1e0d7d46a64e25dfb2a69cfbd9917ccf20e80713`
- Update script permissions
    - `cd tak-server`
    - `chmod -R a+x scripts/`
- Run the setup script
    - `./scripts/setup.sh`
- Wait a while and it should set up
    - If any errors occur during the setup process
    - Reinstall Ubuntu 24.04 and try again
- Update your web browser certs
    - For Firefox:
        - `Settings -> Privacy and Security`
        - Scroll down to `Security -> Certificates`
        - Click `View Certificates`
        - Click `Your Certificates`
        - Click `Import...`
        - Select the `admin.p12` file under `tak-server/tak/certs/files`
        - Click `Authorities`
        - Under `TAK` select `CRFtakserver` 
        - Click `Edit Trust...`
        - Check the `This certificate can identify websites.` box
- Go to the Admininstration webpage
    - `https://localhost:8443`
        - Use the full url, don't try `localhost:8443`
    - Advance through the warnings from Firefox
- Add a User `user1`
    - Click the hamburger in the top-right
        - `Administrative -> Manage Users`
        - Click `Add User`
        - Set `user1` as the Username
        - Set anything as the Password
- Add the `user1` certificate files to the End User Device (your TAK Client)
    - Copy the `user1.p12` file and `truststore-root.p12` files onto a USB drive
        - these files are under `tak-server/tak/certs/files`
    - Copy the files onto your End User Device (EUD)
    - Open up the ATAK app on your EUD
        - Click the triple dot menu on the top-right
        - Scroll down and click `Settings -> TAK Servers`
        - Click the triple dot menu on the top-right
            - Select `Add`
        - Type in any name for your server
        - Type in the IP address of your server
        - Check `SSL` for `Streaming Protocol`
        - `Server Port` should be `8089`
        - Uncheck the `Use default SSL/TLS Certificates`
        - Click `Import Trust Store`
            - Select `truststore-root.p12`
            - Enter the `Password` as `atakatak`
        - Click `Import Client Certificate`
            - Select `user1.p12`
            - Enter the `Password` as `atakatak`
        - Click `OK`


