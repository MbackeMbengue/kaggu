from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

# Colle ici un court extrait (traduction) d'un écrit que tu connais bien
SOURCE = """
Ô vous les adolescents ! ne vous préoccupez que de droiture, évertuez-vous à la
recherche du savoir.
Efforcez-vous d’assimiler et de réviser (vos leçons), fuyez les assemblées qui
entraînent la perdition.
Attachez-vous à quelqu’un qui ne cesse d’adorer son SEIGNEUR, afin qu’il vous
guide dans Sa Voie Droite.
Quiconque se hâte dans sa jeunesse d’emprunter le Droit Chemin, bénéficiera de
la quiétude quand il sera grand.
Celui qui compense ce qu’il a perdu dans la vanité et se consacre à vivifier le
temps,
Par un repentir sincère, se tournant résolument vers DIEU, atteindra la
perfection.
Attachez-vous à ces conseils que je vous prodigue, vous aurez alors un bénéfice
certain Ici-bas et dans l’Au-delà, en compagnie des bienheureux.
"""

consigne = (
    "Tu réponds UNIQUEMENT à partir du texte source fourni. "
    "Si la réponse n'y figure pas, dis clairement : "
    "« Je ne trouve pas cela dans le texte fourni. » "
    "N'invente rien. "
    "Si le texte n'aborde le sujet que partiellement, indique ce qu'il en dit et précise ce qu'il ne dit pas. "
)

question = input("Ta question : ")

reponse = client.models.generate_content(
    model="gemini-3.6-flash",
    config=types.GenerateContentConfig(
        system_instruction=consigne,
        temperature=0.1,  # faible = plus fidèle au texte
    ),
    contents=f"TEXTE SOURCE :\n{SOURCE}\n\nQUESTION : {question}",
)

print(reponse.text)