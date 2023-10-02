import { React, useState, useEffect } from 'react';

import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';

import {
  Divider,
  Typography,
  Grid,
  Paper,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  tableCellClasses,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TableRow,
  CardContent,
  Tab,
  Chip,
  CircularProgress
} from '@mui/material';

import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';

import { CopyBlock, github } from 'react-code-blocks';

const CodeSnippet = () => {
  const [value, setValue] = useState('1');

  const codeTheme = github;

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <>
      <h6 style={{ fontWeight: 'bold', marginTop: '10px', marginBottom: '10px' }}>
        Code examples for sending events
      </h6>
      <Box
        sx={{
          width: '100%',
          typography: 'body1',
          border: '1px solid lightgrey',
          borderRadius: '5px',
          fontSize: '14px'
        }}
      >
        <TabContext value={value}>
          <div sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <TabList onChange={handleChange} aria-label="lab API tabs example">
              <Tab label="Java" value="1" />
              <Tab label="Shell" value="2" />
              <Tab label="Javascript" value="3" />
              <Tab label="Go" value="4" />
              <Tab label="Python" value="5" />
            </TabList>
          </div>

          <TabPanel value="3">
            <CopyBlock
              language="javascript"
              text={`import axios from 'axios';

const options = {
  method: 'POST',
  url: 'https://ingest.drdroid.io/e/ingest/events/v1',
  headers: {
    'Content-Type': 'application/json',
    Authorization: 'Bearer <api_key>'
  },
  data: {
    name: 'payment_started',
    payload: {
      transaction_id: 'si_LULhDM2vvvt7yZ',
      amount: 54.8,
      currency: 'usd',
      invoice_id: 'in_1KnN0G589O8KAxCGfVSpD0Pj'
    }
  }
};

axios.request(options)
  .then(function (response) {
    console.log(response.data);
  })
  .catch(function (error) {
    console.error(error);
  });`}
              codeBlock
              theme={codeTheme}
              showLineNumbers={false}
            />
          </TabPanel>

          <TabPanel value="2">
            <CopyBlock
              language="perl"
              text={`curl --request POST \
--url https://ingest.drdroid.io/e/ingest/events/v1 \
--header 'Authorization: Bearer <api_key>' \
--header 'Content-Type: application/json' \
--data '
{
     "name": "payment_started",
     "payload": {
          "transaction_id": "si_LULhDM2vvvt7yZ",
          "amount": 54.8,
          "currency": "usd",
          "invoice_id": "in_1KnN0G589O8KAxCGfVSpD0Pj"
     }
}
'`}
              codeBlock
              theme={codeTheme}
              showLineNumbers={false}
            />
          </TabPanel>

          <TabPanel value="1">
            <CopyBlock
              language="java"
              text={`OkHttpClient client = new OkHttpClient();

MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\"name\":\"payment_started\",\"payload\":{\"transaction_id\":\"si_LULhDM2vvvt7yZ\",\"amount\":54.8,\"currency\":\"usd\",\"invoice_id\":\"in_1KnN0G589O8KAxCGfVSpD0Pj\"}}");
Request request = new Request.Builder()
  .url("https://ingest.drdroid.io/e/ingest/events/v1")
  .post(body)
  .addHeader("Content-Type", "application/json")
  .addHeader("Authorization", "Bearer <api_key>")
  .build();

Response response = client.newCall(request).execute();`}
              codeBlock
              theme={codeTheme}
              showLineNumbers={false}
            />
          </TabPanel>

          <TabPanel value="4">
            <CopyBlock
              language="go"
              text={`package main
import (
    "fmt"
    "strings"
    "net/http"
    "io/ioutil"
)

func main() {
    url := "https://ingest.drdroid.io/e/ingest/events/v1"
    payload := strings.NewReader("{\"name\":\"payment_started\",\"payload\":{\"transaction_id\":\"si_LULhDM2vvvt7yZ\",\"amount\":54.8,\"currency\":\"usd\",\"invoice_id\":\"in_1KnN0G589O8KAxCGfVSpD0Pj\"}}")
    req, _ := http.NewRequest("POST", url, payload)
    req.Header.Add("Content-Type", "application/json")
    req.Header.Add("Authorization", "Bearer <api_key>")
    res, _ := http.DefaultClient.Do(req)

    defer res.Body.Close()
    body, _ := ioutil.ReadAll(res.Body)
}`}
              codeBlock
              theme={codeTheme}
              showLineNumbers={false}
            />
          </TabPanel>

          <TabPanel value="5">
            <CopyBlock
              language="python"
              text={`import requests
url = "https://ingest.drdroid.io/e/ingest/events/v1"
payload = {
    "name": "payment_started",
    "payload": {
        "transaction_id": "si_LULhDM2vvvt7yZ",
        "amount": 54.8,
        "currency": "usd",
        "invoice_id": "in_1KnN0G589O8KAxCGfVSpD0Pj"
    }
}
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <api_key>"
}
response = requests.post(url, json=payload, headers=headers)`}
              codeBlock
              theme={codeTheme}
              showLineNumbers={false}
            />
          </TabPanel>
        </TabContext>
      </Box>
    </>
  );
};

export default CodeSnippet;
