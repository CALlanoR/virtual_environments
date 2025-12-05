import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

information = """
Akira Toriyama (Toriyama Akira?, Nagoya, Prefectura de Aichi, 5 de abril de 1955-1 de marzo de 2024) fue un mangaka y diseñador de personajes japonés. Primero alcanzó reconocimiento popular tras crear la serie de manga Dr. Slump, y actuar como diseñador de personajes para videojuegos, tales como la serie Dragon Quest, Chrono Trigger y Blue Dragon. Toriyama es considerado uno de los autores más importantes en la historia del manga, especialmente por la creación de Dragon Ball.[1]​ Autores como Eiichirō Oda y Masashi Kishimoto lo han citado como referente e inspiración para sus obras.[2]​[3]​

Ganó el Premio Shogakukan Manga de 1981 al mejor manga shōnen con Dr. Slump, el cual llegó a vender más de 35 millones de copias en Japón. Fue adaptado en una exitosa serie de anime, con una segunda serie creada en 1997, 13 años después de que el manga terminara. Su próxima serie, Dragon Ball, se convertiría en uno de los mangas más populares y exitosos del mundo. Con unas ventas de 260 millones de copias en todo el mundo, es una de las series de manga más vendidas de todos los tiempos y se considera una de las principales razones del auge del manga en la década de 1980 y mediados de la década de 1990. En el extranjero, las adaptaciones de anime de Dragon Ball han sido más exitosas que el manga y se les atribuye el impulso de la popularidad del anime en el mundo occidental. En 2019, Toriyama fue condecorado con la Orden de las Artes y las Letras, por sus contribuciones al arte. 
"""

def main():
    print("Hello from ice-breaker!")
    api_key = os.environ.get('API_KEY')

    summary_template = """
        given the information {information} about a person from I want you to create:
        1. a short summary
        2. tow interesting facts about them
    """
    summary_prompt_template = PromptTemplate(
        input_variables=["information"],
        template=summary_template
    )

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-3.5-turbo"
    )

    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-flash",
    #     temperature=0.7
    # )

    chain = summary_prompt_template | llm

    res = chain.invoke(
        input={
            "information": information
        }
    )

    print(res)

if __name__ == "__main__":
    main()
