# discord-git-bot 

A poorly written Discord bot that tracks latest changes in a repository. Sends out a message every minute.

I swear I meant for this to be a simple Python script. I never intended to turn this into such a spaghetti. 

# Bot in Action 

![bot](https://user-images.githubusercontent.com/61002244/124217692-4d5adb80-dae8-11eb-85b0-fd63157e2f2d.png)


# Example Configuration 

```
[bot]
token = 222ccc333
channel = 1234567

[target]
repo = "https://api.github.com/repos/YOUR_USRNAME/REPO_NAME"
token = 111aabbbcc

[other]
timezone = "America/Anchorage"
```

## `bot` 

- `token`: Your Discord app token 
- `channel`: Channel ID of the channel you want the bot to join (integer) 

## `target` 

- `repo`: Your repository's API URL
- `token`: Your Github app token 

## `other`
- `timezone`: Timezone




