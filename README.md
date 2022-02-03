# ansible-deploy
However ansible is a great tool for IT infrastructure automation in certain cases it's hard to use
it for the complete deployment, because of that tools like ansible-tower/AWX try to wrap it's
activity making further assumptions on the way ansible code is stored (versioning repository), the
way it's executed - certain combinations of inventory/playbook/tag options used to achieve specific
goals. Having it in mind ansible-deploy may be treated as yet another ansible-playbook wrapper, but
focused on comprehensive command line intrface and easy YAML based configuration.

##Some main fatures are
- The results of whole excution are logged and saved together with the ansible code state for
potential review in the future.
- Only one active ansible-deploy per ansible inventory is allowed, attempt to execute ansible-deploy
on already locked infrastructure will be rejected.
- Working directory is setup per every execution of ansible-deploy separately to store the code
state used. This is done by site configurable hook.
- It's possible to lock/unlock inventory (defined as --infra --stage pairs) for manual manipulation,
stopping ansible-deploy from being used.

##Configuration files
- `tasks.yaml` - Configuration of tasks (sets of playbooks to be executed)
- `infra.yaml` - Configuration of infrastructures and stages of those mapping to ansible inventory

##Examples
```
ansible-deploy run --task updateUsers --infra webServers --stage prod
```
