const express = require("express")
const  OpenAIApi  = require("openai")
const cors = require("cors");
const bodyParser = require("body-parser");
require("dotenv").config();

const app = express()
app.use(bodyParser.json());
app.use(cors());

const openai = new OpenAIApi({
    apiKey: "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"
  })

app.listen(8000, ()=>{
  console.log(`servcer running on port: 8000`)
})

app.post('/completions',async (req, res) => {
    try{
        console.log("completions1")
        const completions = await openai.ChatCompletion.create({
        model: "gpt-3.5-turbo",
        messages: [{ role: "system", content: "You are a helpful assistant that generates SQL requests." },{
            role: "user", 
            content: "Create a SQL request to " + req.body.message
        }]
        }) 
        console.log("completions")
        res.send(completions.data.choices[0].message)
    } catch (error){
        console.log(error)
        res.status(500).send('Server Error')
    }  
  })