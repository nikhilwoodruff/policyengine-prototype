'use client';

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";

function submitJob(jobDetails: string) {
  // Convert to JSON
  const job = {
    "options": JSON.parse(jobDetails),
  };
  // Send job to server
  fetch("http://127.0.0.1:8000/job", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(job),
  });
}

export default function Home() {
  const [jobDetails, setJobDetails] = useState<string>("");
  return (
    <div className="h-screen flex justify-center items-center">
      <Card className="h-3/4 w-1/4 p-4 m-4">
        <h1 className="text-2xl font-bold">Start job</h1>
        <p className="text-gray-600">Create a simulation job here.</p>
        <Textarea className="w-full h-1/2" placeholder="Enter job details here" value={jobDetails} onChange={(e) => setJobDetails(e.target.value)} />
        <Button className="w-full" onClick={() => submitJob(jobDetails)}>Start job</Button>
      </Card>
      <Card className="h-3/4 w-3/4 p-4 m-4">
        <h1 className="text-2xl font-bold">Job results</h1>
        <p className="text-gray-600">Results will appear here.</p>
        <p>{jobDetails}</p>
      </Card>
    </div>
  );
}
