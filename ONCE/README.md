These scripts are for testing Calm APIs for the One Click Experience (ONCE) templates. They assume that Calm is enabled and a project has been created. They can be run from anywhere. Don't forget to edit the scripts to update the variables to match your environment.

The scripts do the following and can be modified to suit your needs. The purpose of these scripts were to test out the Calm APIs to preconfigure an environment so a  user could simply login and launch a marketplace item without any configuration.

1. Configure the project with the Nutanix provider and specified subnet
2. Configure the project environment with credentials and VM settings
3. Import blueprints (the blueprints must exist on the machine the scripts are run from)
4. Configure the blueprints with credentials, secret keys, and the appropriate disk image and NIC
5. Submit a blueprint to the marketplace for approval
6. Approve the blueprint
7. Publish the blueprint to the marketplace
