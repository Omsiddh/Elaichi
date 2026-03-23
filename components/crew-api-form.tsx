"use client"
import React, { useState, FormEvent } from 'react';

interface CrewApiFormProps {
  baseUrl: string;
  bearerToken: string;
  className?: string;
}

interface LastStep {
  thought: string;
  action: string;
  actionInput: string;
  actionResult: string;
  result?: string;
}

const CrewApiForm: React.FC<CrewApiFormProps> = ({ baseUrl, bearerToken, className }) => {
  
  const [taskId, setTaskId] = useState<string>('');
  const [state, setState] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [lastStep, setLastStep] = useState<LastStep | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    try {
      const kickoffResponse = await fetch(`${baseUrl}/kickoff`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${bearerToken}`
        },
        body: JSON.stringify({
          inputs: {
            
          }
        })
      });
      const kickoffData = await kickoffResponse.json();
      setTaskId(kickoffData.kickoff_id);
      pollStatus(kickoffData.kickoff_id);
    } catch (error) {
      console.error('Error starting crew:', error);
      setIsLoading(false);
    }
  };

  const parseLastStep = (lastStep: { action: string; result: string }): LastStep => {
    const thoughtMatch = lastStep.action.match(/Thought:\s*(.*?)\s*(?=(Action:|$))/s);
    const actionMatch = lastStep.action.match(/Action:\s*(.*?)\s*(?=(Action Input:|$))/s);
    const actionInputMatch = lastStep.action.match(/Action Input:\s*(.*)/s);
    const resultInputMatch = lastStep.action.match(/Result:\s*(.*)/s);

    const thought = thoughtMatch ? thoughtMatch[1].trim() : '';
    const action = actionMatch ? actionMatch[1].trim() : '';
    const actionInput = actionInputMatch ? actionInputMatch[1].trim() : '';
    const actionResult = resultInputMatch ? resultInputMatch[1].trim() : '';

    return { thought, action, actionInput, actionResult, result: lastStep.result };
  };

  const pollStatus = async (id: string) => {
    try {
      const statusResponse = await fetch(`${baseUrl}/status/${id}`, {
        headers: {
          'Authorization': `Bearer ${bearerToken}`
        }
      });
      const statusData = await statusResponse.json();
      setState(statusData.state);
      setStatus(statusData.status);
      setLastStep(statusData.last_step ? parseLastStep(statusData.last_step) : null);
      setResult(statusData.result);

      if (statusData.state === 'SUCCESS') {
        setIsLoading(false);
      } else {
        setTimeout(() => pollStatus(id), 10000);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
      setTimeout(() => pollStatus(id), 10000);
    }
  };

  return (
    <div className={`p-4 bg-white rounded shadow ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
      
        
        <div>
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.963 7.963 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              'Start Crew'
            )}
          </button>
        </div>
      </form>
      {taskId && state !== 'SUCCESS' && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg shadow-inner">
          <p className="text-sm text-gray-500"><strong>Task ID:</strong> {taskId}</p>
          <p className="text-sm text-gray-500"><strong>State:</strong> {state}</p>
          <p className="text-sm text-gray-500"><strong>Status:</strong> {status}</p>
        </div>
      )}

      {status && status !== 'SUCCESS' && lastStep && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg shadow-inner">
          <h4 className="text-md font-medium text-gray-700">Last Step Details</h4>
          {lastStep.thought && (
            <p className="text-sm text-gray-500 mt-5">
              <strong>Thought:</strong><br/>
              <pre className="inline whitespace-pre-wrap">{lastStep.thought}</pre>
            </p>
          )}
          {lastStep.action && (
            <p className="text-sm text-gray-500 mt-5">
              <strong>Action:</strong><br/>
              <pre className="inline whitespace-pre-wrap">{lastStep.action}</pre>
            </p>
          )}
          {lastStep.actionInput && (
            <p className="text-sm text-gray-500 mt-5">
              <strong>Action Input:</strong>
              <br />
              <pre className="inline whitespace-pre-wrap">{lastStep.actionInput}</pre>
            </p>
          )}
          {lastStep.result && (
            <p className="text-sm text-gray-500 mt-5">
              <strong>Action Result:</strong><br/>
              <pre className="inline whitespace-pre-wrap">{lastStep.result}</pre>
            </p>
          )}
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg shadow-inner">
          <h3 className="text-sm font-medium text-gray-700">Final Result</h3>
          <div className="text-sm text-gray-500 break-words whitespace-pre-wrap">{result}</div>
        </div>
      )}
    </div>
  );
};

export default CrewApiForm;