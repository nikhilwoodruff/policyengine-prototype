'use client';

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";

import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.SUPABASE_URL || '', process.env.SUPABASE_KEY || '');
const apiUrl = process.env.API_LOCAL_URL || '';

async function submitJob(jobDetails: string) {
  // Convert to JSON
  const job = {
    "options": JSON.parse(jobDetails),
  };
  // Send job to server
  return fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(job),
  }).then((response) => response.json()).then(
    data => data.id
  )
}

export default function Home() {
  const [jobDetails, setJobDetails] = useState<string>("");
  const [jobId, setJobId] = useState<string>("");
  /* eslint-disable @typescript-eslint/no-explicit-any */
  const [jobData, setJobData] = useState<any>(null);
  return (
    <div className="h-screen flex justify-center items-center">
      <Card className="h-3/4 w-1/4 p-4 m-4">
        <h1 className="text-2xl font-bold">Start job</h1>
        <p className="text-gray-600">Create a simulation job here.</p>
        <Textarea className="w-full h-1/2" placeholder="Enter job details here" value={jobDetails} onChange={(e) => setJobDetails(e.target.value)} />
        <Button className="w-full" onClick={() => submitJob(jobDetails).then(value => {
            setJobId(value);
            supabase.channel(`job_${value}`).on(
              "postgres_changes", 
              { schema: "public", table: "job", event: "*", filter: "id=eq." + value },
              (payload) => {
                console.log("Change received!", payload);
                setJobData(payload);
              }
            ).subscribe();

          })}>Start job</Button>
      </Card>
      <Card className="h-3/4 w-3/4 p-4 m-4">
        <h1 className="text-2xl font-bold">Job results</h1>
        <p className="text-gray-600">Results will appear here.</p>
        <h4>Job {jobId}</h4>
        <p>{jobData?.new?.result ? JSON.stringify(jobData.new.result) : ""}</p>
      </Card>
    </div>
  );
}
