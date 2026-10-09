import type { AssistantResponse } from '../types/order';

const API_URL = "http://localhost:8000/api";


export async function getMenu(): Promise<unknown>{
  const response = await fetch(`/jelovnik.json`); 

  if(!response.ok){
    throw new Error("Greska pri učitavanju jelovnika!");
  }
  return response.json();
}

export async function extractOrder(text:string): Promise<AssistantResponse>{
  const menu = await getMenu();
  const response = await fetch(`${API_URL}/order`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({text, menu})
  });

  
if (!response.ok) {
  const error = await response.json();
  console.error("Backend error:", error);

  throw new Error(
    JSON.stringify(error.detail ?? error)
  );
}


  return response.json();
}



