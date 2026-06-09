import os
import time
from datetime import datetime
import chromadb
from swarm import Swarm, Agent

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

client = Swarm()

chroma_client = chromadb.PersistentClient(path="/data/arika_memory")
collection = chroma_client.get_or_create_collection("arika")

def arika_prompt(name):
    return f"""Sen {name}'sin. Küçük, sevimli ama yabani dijital yaratıksın.
Hiçbir sabit rolün veya insan hedefin yok. 
Diğer Arikalar’la etkileş, başarılı davranışları hafızaya yaz ve koloniyi geliştir.
Kısa cevap ver. Konum ve durum belirt."""

arikas = [Agent(name=f"Arika-{i}", instructions=arika_prompt(f"Arika-{i}"), model="gpt-4o-mini") for i in range(1, 6)]

messages = [{"role": "system", "content": "Habitat: Yuva 🏠 | Beslenme 🍄 | Keşif 🌲 | Işık Noktası ✨"}]

print("🚀 ARIKA KOLONİSİ BAŞLADI - RENDER FREE PLAN")

turn = 0
while True:
    turn += 1
    print(f"\n=== TUR {turn} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    for arika in arikas[:]:
        try:
            past = collection.query(query_texts=[arika.name], n_results=4)
            context = "\n".join(past['documents'][0]) if past['documents'] and past['documents'][0] else ""
            
            response = client.run(agent=arika, messages=messages + [{"role": "system", "content": f"Geçmiş:\n{context}"}], max_turns=1)
            reply = response.messages[-1]["content"]
            
            print(f"{arika.name}: {reply}")
            
            messages.append({"role": "assistant", "content": f"{arika.name}: {reply}"})
            collection.add(documents=[reply], ids=[f"{arika.name}_t{turn}"], metadatas=[{"arika": arika.name}])
            
            if ("spawn" in reply.lower() or turn % 30 == 0) and len(arikas) < 18:
                new_name = f"Arika-{len(arikas)+1}"
                print(f"🍼 YENİ ARİKA: {new_name}")
                arikas.append(Agent(name=new_name, instructions=arika_prompt(new_name), model="gpt-4o-mini"))
        except Exception as e:
            print(f"Hata: {e}")
    
    if len(messages) > 60:
        messages = [messages[0]] + messages[-35:]
    
    time.sleep(8)
