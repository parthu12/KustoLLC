import {useState} from 'react'
interface ChatData  {
  role: string,
  content: string
}

const App = ()=> {
   
  const [value, setValue] = useState<string>("")
  const [value1, setValue1] = useState<string>("")
  const [chat, setChat] = useState<any>([])

const getQuery = async ()=>{
  try{
    const options = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: value, table: value1})
    };
    console.log("options", options)
    const response = await fetch("http://localhost:8000/completions", options )
    const data = await response.json()
    const useMessage = {
      role: "user",
      content: value
    }
    setChat((oldData:any) => [...oldData, data , useMessage])

  } catch(error){
  console.log(error)
  }
}

const clearChat = ()=>{
  setValue("");
  setChat([]);
  setValue1("");
}

  const latestCode = chat.filter((message: ChatData) => message.role === "assistant").pop()
 
  return (
    <div className="app">
      <input value={value} onChange={e => setValue(e.target.value)}/>
      <input value={value1} onChange={e => setValue1(e.target.value)}/>
      
      <div className="code-display">
      <div className="buttons">
        <div className="button first"></div>
        <div className="button middle"></div>
        <div className="button last"></div>
      </div>

      <div className="code-output">
        <p>{latestCode?.content|| ""}</p>
      </div>

      </div>

      <div className="button-container">
        <button id="get-query" onClick={getQuery}>Get Query!</button>
        <button id="clear-chat" onClick={clearChat}>Clear Chat</button>
      </div>
      
    </div>
  );
}

export default App;