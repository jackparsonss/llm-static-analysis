# LLM-Static-Analysis

## Step 1: Build Your Virtual Environment
```
make build
```

## Step 2: Add OpenAI Credentials to `.env` file
```

ORG_ID=<ORG_ID>
OPENAI_API_KEY=<API_KEY>
```

## Step 3: Fetch Data(this could take a while)
```
make fetch
```

## Step 4: Download and Filter the data
```
make data 
```

## Step 5: Run Test Experiment
```
make experiment
```

## Cleaning Folders
Running the experiment lots of times will result in a lot of `<time>_output/` folders, this command will delete them all
