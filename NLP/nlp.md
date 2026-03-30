Fases del procesamiento del lenguaje natural (PLN)
Última actualización: 23 de julio de 2025
El Procesamiento del Lenguaje Natural (PLN) ayuda a los ordenadores a comprender, analizar e interactuar con el lenguaje humano. Implica una serie de fases que trabajan juntas para procesar el lenguaje y cada fase ayuda a comprender la estructura y el significado del lenguaje humano. En este artículo, entenderemos estas fases.

Fases de PLN
Fases de la PLN
1. Análisis léxico y morfológico
Análisis léxico
Se centra en identificar y procesar palabras (o lexemas) en un texto. Descompone el texto de entrada en tokens individuales que son unidades significativas de lenguaje, como palabras o frases.

Tareas clave en el análisis léxico:

Tokenización: Proceso de dividir un texto en fragmentos más pequeños llamados tokens. Por ejemplo, la frase "Me encanta programar" se tokenizaría en ["yo", "amor", "programación"].
Etiquetado de partes gramaticales: Asignar partes gramaticales como sustantivo, verbo o adjetivo a cada símbolo de la oración. Esto nos ayuda a entender los roles gramaticales de las palabras en el contexto.
Ejemplo: Considera la frase: "Estoy leyendo un libro."

Tokenización: La oración se divide en tokens o palabras individuales: ["Yo", "soy", "leyendo", "a", "libro"]
Etiquetado de Parte del Discurso: A cada token se le asigna una categoría gramatical: ["I" → Pronombre (PRP), "am" → Verbo (VBP), "reading" → Verb (VBG), "a" → Artículo (DT), "book" → sustantivo (NN)]
Importancia del análisis léxico

Identificación de palabras: Descompone el texto en tokens, lo que ayuda al sistema a entender palabras individuales para su procesamiento posterior.
Simplificación del texto: Simplifica el texto mediante tokenización y stemming, lo que mejora la precisión en las tareas de PLN.
Análisis morfológico
Trata sobre morfemas, que son las unidades de significado más pequeñas en una palabra. Es importante para entender la estructura de las palabras y sus partes identificando morfemas libres (palabras independientes como "cat") y morfemas ligados (como prefijos o sufijos, por ejemplo "un-" o "-ing").

Tareas clave en el análisis morfológico:

Stemming: Reducir palabras a su forma raíz como "running" a "run".
Lemmatization: Converting words to their base or dictionary form considering the context like "better" becomes "good".
Importance of Morphological Analysis

Understanding Word Structure: It helps in breaking the composition of complex words.
Improving Accuracy: It enhances accuracy of tasks such as part-of-speech tagging, syntactic parsing and machine translation.
By identifying and analyzing morphemes system can identify text correctly at the most basic level which helps in more advanced NLP applications.

2. Syntactic Analysis (Parsing)
Syntactic Analysis helps in understanding how words in a sentence are arranged according to grammar rules. It ensures that the sentence follows correct grammar which makes the meaning clearer. The goal is to create a parse tree which is a diagram showing the structure of sentence. It breaks the sentence into parts like the subject, verb and object and shows how these parts are connected. This helps machines understand the relationships between words in the sentence.

Key components of syntactic analysis include:
POS Tagging: Assigning parts of speech (noun, verb, adjective) to words in a sentence as discussed earlier.
Ambiguity Resolution: Handling words that have multiple meanings (e.g "book" can be a noun or a verb).
Examples
Consider the following sentences:

Correct Syntax: "John eats an apple."
Sintaxis incorrecta: "La manzana se come a John."
A pesar de usar las mismas palabras, solo la primera frase es gramaticalmente correcta y tiene sentido. La correcta disposición de las palabras según las reglas gramaticales es lo que hace que la frase tenga sentido. Al analizar la estructura de las oraciones, los sistemas de PLN pueden comprender y generar mejor el lenguaje humano. Esto ayuda en tareas como la traducción automática, el análisis de sentimientos y la recuperación de información, al hacer el texto más claro y reducir la confusión.

3. Análisis Semántico
El análisis semántico se centra en comprender el significado detrás de palabras y oraciones. Garantiza que el texto no solo sea gramaticalmente correcto, sino también lógicamente coherente y relevante en el contexto. Su objetivo es comprender las definiciones de palabras en diccionario y su uso en contexto, así como determinar si la disposición de las palabras en una oración tiene sentido lógico.

Tareas clave en el análisis semántico
Reconocimiento de Entidades Nombradas (NER): Identifica y clasifica entidades como nombres de personas, ubicaciones, organizaciones, fechas y más. Estas entidades aportan un significado importante al texto y ayudan a comprender el contexto. Por ejemplo, en la frase "Tesla anunció su nuevo vehículo eléctrico en California", NER identificaría "Tesla" como organización y "California" como ubicación.
Desambiguación del sentido de palabras (WSD): Muchas palabras tienen múltiples significados dependiendo del contexto en el que se utilicen. Identifica el significado correcto de una palabra basándose en el texto que la rodea. Por ejemplo, la palabra "bank" puede referirse a una institución financiera o a la orilla de un río. Utiliza el contexto para identificar qué significado se aplica en una oración dada, lo que garantiza que la interpretación sea precisa.
Ejemplo de análisis semántico
"La manzana se come un pata." Aunque gramaticalmente correcta, esta frase no tiene sentido semánticamente porque una manzana no puede "comerse" a una persona. El análisis semántico asegura que el significado sea lógicamente correcto y contextualmente apropiado. Es importante para diversas aplicaciones de PLN, incluyendo la traducción automática, la recuperación de información y la respuesta a preguntas.

4. Integración del discurso
Es el proceso de entender cómo frases individuales o segmentos de texto se conectan y se relacionan entre sí dentro de un contexto más amplio. Esta fase garantiza que el significado de un texto sea consistente y coherente a lo largo de varias frases o párrafos. Es importante para entender textos largos o complejos donde el significado se centra en afirmaciones previas.

Aspectos clave de la integración del discurso:
Resolución de anáfora: La anáfora se refiere al uso de pronombres u otras referencias que dependen de partes anteriores del texto. Por ejemplo, en la frase "Taylor fue a la tienda. Ella compró la compra" el pronombre "Ella" hace referencia a "Taylor". Garantiza que referencias como estas se entiendan correctamente vinculándolas a sus antecedentes.
Referencias contextuales: Muchas palabras o frases solo pueden entenderse plenamente si se consideran en el contexto de las frases siguientes. Ayuda a interpretar cómo ciertas palabras o frases se centran en el contexto. Por ejemplo, "Fue un gran día" queda más claro cuando sabes qué evento o situación se está discutiendo.
Ejemplo de integración del discurso
"Taylor went to the store to buy some groceries. She realized she forgot her wallet." Understanding that "Taylor" is the antecedent of "she" is important for understanding sentence's meaning.
"This is unfair!" helps in understand what "this" refers to we need to identify following sentences. Without context statement's meaning remains unclear.
It is important for NLP applications like machine translation, chatbots and text summarization. It ensures that meaning remains same across sentences which helps machines to understand context. This enables accurate and natural responses in applications like conversational AI and document translation.

5. Pragmatic Analysis
Pragmatic analysis helps in understanding the deeper meaning behind words and sentences by looking beyond their literal meanings. While semantic analysis looks at the direct meaning it considers the speaker's or writer's intentions, tone and context of the communication.

Key tasks in pragmatic analysis:
Understanding Intentions: Sometimes language doesn’t mean what it says literally. For example when someone asks "Can you pass the salt?" it's not about ability but a polite request. It helps to understand true intention behind such expressions.
Figurative Meaning: Language often uses idioms or metaphors that can’t be taken literally.
Ejemplos de análisis pragmático
"¡Hola! ¿Qué hora es?" aquí puede ser una petición sencilla para la hora actual, pero también podría implicar preocupación por llegar tarde.
Por ejemplo, "Me estoy enamorando de ti" significa "te quiero", no literalmente caer. Ayuda a interpretar estos significados no literales.
Es importante para tareas de PLN como el análisis de sentimientos, chatbots e IA basada en conversaciones. Ayuda a las máquinas a entender las intenciones, el tono y el contexto del hablante, que van más allá del significado literal de las palabras. Al identificar sarcasmo y emociones, esto ayuda a que los sistemas respondan de forma natural, lo que mejora la interacción humano-ordenador. Al combinar estas fases, los sistemas de PLN pueden interpretar, analizar y generar el lenguaje humano de forma eficaz, creando interacciones más inteligentes y naturales entre humanos y máquinas.

El futuro del procesamiento del lenguaje natural: tendencias e innovaciones
Última actualización: 23 de julio de 2025
No hay razones por las que el mundo actual esté entusiasmado al ver innovaciones como ChatGPT y despliegues de GPT/NLP (Procesamiento de Lenguaje Natural), conocidos como el momento definitorio de la historia de la tecnología en el que finalmente podemos crear una máquina capaz de imitar la reacción humana. Si alguien te hubiera dicho hace unos años que hay una máquina, nadie te habría creído. Pero ahora aquí tenemos chatGPT, que puede construir cualquier cosa dentro de todo.

Tendencias e innovaciones del PLN

¿Qué es el PLN?
El PLN es una de las aplicaciones de la IA que analiza un lenguaje natural. Se refiere al método de inteligencia artificial para comunicarse con un sistema inteligente utilizando lenguaje natural. La aplicación real del PLN se puede ver en nuestros asistentes virtuales como Siri, Google Assistant, etc. Todos sabemos que estos asistentes virtuales en nuestro móvil no son un humano hablándonos, es simplemente una estructura robótica, sino cómo una máquina puede hablar y comportarse como un humano. Esta capacidad ha sido generada por el PLN (procesamiento del lenguaje natural). Es una habilidad que enseñó a una máquina a responder, leer y entender el lenguaje humano para que pueda comunicarse con nosotros sobre su problema interno. Combina el campo de la lingüística y la informática para descifrar pautas estructuradas de lenguaje y crear un modelo de aprendizaje automático capaz de comprender y descomponer aspectos significativos de las oraciones.

Hay 7 pasos básicos mediante los cuales una máquina puede procesar el lenguaje natural, que son los siguientes

Segmentación - Es un proceso de división de oraciones complejas en oraciones más pequeñas.
Tokenización - Es el proceso de descomponer frases simples en palabras.
Palabras clave - Las palabras que no desempeñan un papel importante en la generación de un significado a la oración, como y, the, is, etc., se eliminan de las oraciones conocidas como palabras de oclusión.
Stemming - Es el proceso de enseñar un conjunto básico de datos en oraciones que probablemente signifique lo mismo. Por eso se crea conciencia en nuestro sistema.
Lematización - La adición de emociones y estados de ánimo a las palabras para que una máquina pueda comprender la relación emocional de una oración con un humano y así generar una respuesta razonable se llama lematización.
Etiquetado de voz - El proceso de enseñar términos gramaticales básicos como sustantivos, verbos, preposiciones, etc. a una máquina y etiquetar cada palabra de una oración como ese término gramatical se llama etiquetado de habla.
Etiquetado de entidades nombradas - Para entender el sustantivo importante al que se refiere el documento, que son humanos populares como actores, etc., y etiquetarlos se conoce como etiquetado de entidades nombradas.
Con el aumento de la demanda de soluciones de lenguaje automatizado, el mercado laboral actual busca profesionales en PLN. De ahí se crea una tendencia en nuestro análisis del mercado laboral.

Herramientas utilizadas para PLN

1. Regex (Regular Expressions) Library
Regex is a tool for pattern matching and text modification. It helps in data cleaning, extracting useful information and handling text transformation tasks.

Pattern Matching: Identify and remove unwanted characters, symbols or whitespace in large datasets to prepare text for analysis.
Text Extraction: Extract key pieces of information like product IDs or dates from documents or web pages.
Real-life applications
Data Cleaning: Extract and clean contact details such as phone numbers or emails from raw datasets.
Information Extraction: Pull out product identifiers, such as SKUs or financial numbers from reports for further analysis.
2. NLTK (Natural Language Toolkit)
NLTK provides various tools for text analysis. It is used for educational and research purposes which offers features for tokenization, stemming and part-of-speech tagging.

Tokenization: Break down text into smaller, meaningful units like words or sentences.
Stemming and Lemmatization: Simplify words to their root form for more consistent analysis.
Real-life applications
Customer Feedback Analysis: Split reviews into words or sentences for sentiment analysis.
Text Classification: Automatically categorize content like news articles or social media posts.
3. spaCy
spaCy is designed for high-performance text processing. It is good at tasks such as named entity recognition (NER) and dependency parsing which helps in making it ideal for real-time applications.

Named Entity Recognition (NER): Identify and classify entities like names, locations or organizations in text.
Dependency Parsing: Understand the grammatical relationships between words in a sentence.
Real-life applications
Legal Document Analysis: Identify and extract key entities like company names or legal terms from contracts.
Customer Service Automation: Extract relevant details like product names or addresses from customer queries for faster responses.
4. TextBlob
TextBlob is an easy-to-use library that simplifies tasks like sentiment analysis and translation. It's great for those just starting with NLP or for quick prototyping.

Sentiment Analysis: Classify the sentiment of a text as positive, negative or neutral.
Translation: Translate text between languages using pre-trained models.
Real-life applications:
Brand Sentiment Monitoring: Analyze social media posts to get public sentiment about a brand.
Multilingual Customer Support: Translate support tickets or chat messages to facilitate communication across languages.
5. Textacy
Textacy extends spaCy and provides tools for preprocessing, linguistic feature extraction and topic modeling helps in making it useful for deeper text analysis.

Preprocessing: Clean and prepare text by removing unnecessary words, punctuation and formatting.
Topic Modeling: Identify topics within large corpora to understand underlying themes.
Real-life applications:
Market Research: Discover trends and themes in customer feedback or product reviews.
Content Summarization: Summarize long articles or reports by extracting the most important topics.
6. VADER (Valence Aware Dictionary and sEntiment Reasoner)
VADER is a rule-based sentiment analysis tool which is designed for analyzing sentiment in social media and informal text. It uses a specialized lexicon to account for the intensity of sentiment including emojis and slang.

Sentiment Analysis: Checks whether a text conveys positive, negative or neutral sentiment.
Handling Emojis and Slang: Understanding the sentiment behind emojis and informal expressions in social media content.
Real-life applications
Social Media Analysis: Track sentiment in posts or tweets to understand public opinion on a topic.
Customer Feedback Analysis: Monitor product or service reviews for sentiment trends.
7. Gensim
Gensim is used for unsupervised topic modeling and document similarity analysis which helps in making it ideal for discovering patterns in large text corpora.

Topic Modeling: Identify and classify hidden topics within large datasets using models like LDA.
Word Embeddings: Learn vector representations of words to capture their meanings in context.
Real-life applications
Content Recommendation Systems: Suggest articles, products or services based on similar topics.
Document Clustering: Group similar documents together for efficient retrieval.
8. AllenNLP
AllenNLP is built on PyTorch and provides deep learning models for various NLP tasks. It is useful for tasks that require advanced machine learning techniques.

Pre-trained Models: Use pre-trained models for tasks like sentiment analysis and named entity recognition.
Custom Model Training: Train custom models using deep learning tools for specific NLP applications.
Real-life applications
Intelligent Customer Support: Develop AI chatbots to automatically respond to customer queries.
Text Summarization: Automatically generate concise summaries from long documents.
9. Stanza
Stanza developed by Stanford offers pre-trained models for a variety of NLP tasks like tokenization and named entity recognition. It is built on top of PyTorch which makes it efficient and scalable.

Tokenization : Break down text into smaller components like words or phrases.
Dependency Parsing: Analyze sentence structures to understand relationships between words.
Real-life applications
Legal Text Analysis: Extract relevant information from legal documents or case files.
Syntactic Text Analysis: Improve the accuracy of machine learning models by analyzing sentence structure.
10. Pattern
Pattern is a simple library for NLP and web mining with features like part-of-speech tagging and sentiment analysis. It is useful for small projects and learning about NLP.

POS Tagging: Classify words in a sentence into grammatical categories like nouns, verbs or adjectives.
Sentiment Analysis: Find whether the sentiment of text is positive, negative or neutral.
Real-life applications
Basic Text Processing: Analyze small datasets for sentiment classification or part-of-speech tagging.
Web Scraping: Extract text from websites for further analysis or research.
11. PyNLPl
PyNLPl is a library for tasks like syntactic parsing and morphological analysis. It's suitable for complex linguistic analysis, especially for multilingual projects.

Corpus Processing: Efficiently handle and process large text corpora for NLP tasks.
Syntactic Parsing: Break down sentences to understand their grammatical structure.
Real-life applications
Multilingual Text Processing: Analyze text in multiple languages helps in making it useful for global projects.
Linguistic Research: Conduct detailed research on sentence structures and word meanings.
12. Hugging Face Transformer
Hugging Face is known for its transformer-based models such as BERT and GPT. It is used for advanced NLP tasks like text classification, text generation and question answering.

Pre-trained Models: Access pre-trained models like BERT and GPT for various NLP tasks.
Fine-Tuning: Adjust these models to work with specific datasets for better performance on custom tasks.
Real-life applications
AI Assistants: Enhance virtual assistants such as Siri or Alexa to improve responses.
Content Generation: Automatically generate text, like articles based on given input.
13. flair
Flair uses deep learning techniques for tasks such as text classification and named entity recognition. It excels in providing high accuracy.

NER: Extract named entities such as people, places or organizations from text.
Text Classification: Classify documents into predefined categories based on their content.
Real-life applications
News Categorization: Automatically sort articles into categories like politics, health and sports.
Document Classification: Organize legal or academic documents for easy retrieval.
14. FastText
FastText developed by Facebook AI, is designed for fast text classification and word embeddings. It can handle large datasets efficiently.

Text Classification: Classify text into categories quickly even with large datasets.
Word Embeddings: Create vector representations of words to capture semantic meanings and relationships.
Real-life applications
Spam Detection: Automatically identify spam messages in email or chat platforms.
Real-Time Analysis: Analyze customer feedback or social media posts in real time.
15. Polyglot
Polyglot is a multilingual library that supports over 130 languages. It’s ideal for tasks that require language detection, tokenization or sentiment analysis across various languages.

Multilingual Support: Process text data in more than 130 languages.
Language Detection: Automatically detect the language of any given text.
Real-life applications
Multilingual Customer Support: Provide global support by handling customer queries in different languages.
Global Sentiment Analysis: Track sentiment across various languages to gauge worldwide opinions.
By exploring these NLP libraries, we can gain valuable insights from textual data and apply them to solve real-world problems across different fields

Normalizing Textual Data with Python
Last Updated : 23 Jul, 2025
In this article, we will learn How to Normalizing Textual Data with Python. Let's discuss some concepts :

Textual data ask systematically collected material consisting of written, printed, or electronically published words, typically either purposefully written or transcribed from speech.
Text normalization is that the method of transforming text into one canonical form that it'd not have had before. Normalizing text before storing or processing it allows for separation of concerns since the input is sure to be consistent before operations are performed thereon. Text normalization requires being conscious of what sort of text is to be normalized and the way it's to be processed afterwards; there's no all-purpose normalization procedure.
Steps Required

Here, we will discuss some basic steps need for Text normalization.

Input text String,
Convert all letters of the string to one case(either lower or upper case),
If numbers are essential to convert to words else remove all numbers,
Remove punctuations, other formalities of grammar,
Remove white spaces,
Remove stop words,
And any other computations.
We are doing Text normalization with above-mentioned steps, every step can be done in some ways. So we will discuss each and everything in this whole process.

Text String




# input string 
string = "       Python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much Python 2 code does not run unmodified on Python 3. With Python 2's end-of-life, only Python 3.6.x[30] and later are supported, with older versions still supporting e.g. Windows 7 (and old installers not restricted to 64-bit Windows)."
print(string)
Output:


"       Python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much Python 2 code does not run unmodified on Python 3. With Python 2's end-of-life, only Python 3.6.x[30] and later are supported, with older versions still supporting e.g. Windows 7 (and old installers not restricted to 64-bit Windows)."


Case Conversion (Lower Case)

In Python, lower() is a built-in method used for string handling. The lower() methods returns the lowercased string from the given string. It converts all uppercase characters to lowercase. If no uppercase characters exist, it returns the original string.




# input string
string = "       Python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much Python 2 code does not run unmodified on Python 3. With Python 2's end-of-life, only Python 3.6.x[30] and later are supported, with older versions still supporting e.g. Windows 7 (and old installers not restricted to 64-bit Windows)."
​
# convert to lower case
lower_string = string.lower()
print(lower_string)
Output:


"       python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much python 2 code does not run unmodified on python 3. with python 2's end-of-life, only python 3.6.x[30] and later are supported, with older versions still supporting e.g. windows 7 (and old installers not restricted to 64-bit windows)."


Removing Numbers

Remove numbers if they're not relevant to your analyses. Usually, regular expressions are used to remove numbers.




# import regex
import re
​
# input string 
string = "       Python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much Python 2 code does not run unmodified on Python 3. With Python 2's end-of-life, only Python 3.6.x[30] and later are supported, with older versions still supporting e.g. Windows 7 (and old installers not restricted to 64-bit Windows)."
​
# convert to lower case
lower_string = string.lower()
​
# remove numbers
no_number_string = re.sub(r'\d+','',lower_string)
print(no_number_string)
Output:


"       python ., released in , was a major revision of the language that is not completely backward compatible and much python  code does not run unmodified on python . with python 's end-of-life, only python ..x[] and later are supported, with older versions still supporting e.g. windows  (and old installers not restricted to -bit windows)."


Removing punctuation

The part of replacing with punctuation can also be performed using regex. In this, we replace all punctuation by empty string using certain regex.




# import regex
import re
​
# input string 
string = "       Python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much Python 2 code does not run unmodified on Python 3. With Python 2's end-of-life, only Python 3.6.x[30] and later are supported, with older versions still supporting e.g. Windows 7 (and old installers not restricted to 64-bit Windows)."
​
# convert to lower case
lower_string = string.lower()
​
# remove numbers
no_number_string = re.sub(r'\d+','',lower_string)
​
# remove all punctuation except words and space
no_punc_string = re.sub(r'[^\w\s]','', no_number_string) 
print(no_punc_string)
Output:


'       python  released in  was a major revision of the language that is not completely backward compatible and much python  code does not run unmodified on python  with python s endoflife only python x and later are supported with older versions still supporting eg windows  and old installers not restricted to bit windows'


Removing White space

The strip() function is an inbuilt function in Python programming language that returns a copy of the string with both leading and trailing characters removed (based on the string argument passed).




# import regex
import re
​
# input string 
string = "       Python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much Python 2 code does not run unmodified on Python 3. With Python 2's end-of-life, only Python 3.6.x[30] and later are supported, with older versions still supporting e.g. Windows 7 (and old installers not restricted to 64-bit Windows)."
​
# convert to lower case
lower_string = string.lower()
​
# remove numbers
no_number_string = re.sub(r'\d+','',lower_string)
​
# remove all punctuation except words and space
no_punc_string = re.sub(r'[^\w\s]','', no_number_string) 
​
# remove white spaces
no_wspace_string = no_punc_string.strip()
print(no_wspace_string)
Output:


'python  released in  was a major revision of the language that is not completely backward compatible and much python  code does not run unmodified on python  with python s endoflife only python x and later are supported with older versions still supporting eg windows  and old installers not restricted to bit windows'


Removing Stop Words

Stop words” are the foremost common words during a language like “the”, “a”, “on”, “is”, “all”. These words don't carry important meaning and are usually faraway from texts. It is possible to get rid of stop words using tongue Toolkit (NLTK), a set of libraries and programs for symbolic and statistical tongue processing.


# download stopwords
import nltk
nltk.download('stopwords')

# import nltk for stopwords
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
print(stop_words)

# assign string
no_wspace_string='python  released in  was a major revision of the language that is not completely backward compatible and much python  code does not run unmodified on python  with python s endoflife only python x and later are supported with older versions still supporting eg windows  and old installers not restricted to bit windows'

# convert string to list of words
lst_string = [no_wspace_string][0].split()
print(lst_string)

# remove stopwords
no_stpwords_string=""
for i in lst_string:
    if not i in stop_words:
        no_stpwords_string += i+' '
        
# removing last space
no_stpwords_string = no_stpwords_string[:-1]
print(no_stpwords_string)
Output: 



In this, we can normalize the textual data using Python. Below is the complete python program:


# import regex
import re

# download stopwords
import nltk
nltk.download('stopwords')

# import nltk for stopwords
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))


# input string 
string = "       Python 3.0, released in 2008, was a major revision of the language that is not completely backward compatible and much Python 2 code does not run unmodified on Python 3. With Python 2's end-of-life, only Python 3.6.x[30] and later are supported, with older versions still supporting e.g. Windows 7 (and old installers not restricted to 64-bit Windows)."

# convert to lower case
lower_string = string.lower()

# remove numbers
no_number_string = re.sub(r'\d+','',lower_string)

# remove all punctuation except words and space
no_punc_string = re.sub(r'[^\w\s]','', no_number_string) 

# remove white spaces
no_wspace_string = no_punc_string.strip()
no_wspace_string

# convert string to list of words
lst_string = [no_wspace_string][0].split()
print(lst_string)

# remove stopwords
no_stpwords_string=""
for i in lst_string:
    if not i in stop_words:
        no_stpwords_string += i+' '
        
# removing last space
no_stpwords_string = no_stpwords_string[:-1]

# output
print(no_stpwords_string)

Regex Tutorial - How to write Regular Expressions
Last Updated : 22 Dec, 2025
A regular expression (regex) is a sequence of characters that defines a search pattern. It is mainly used for pattern matching in strings, such as finding, replacing, or validating text. Regex is supported in almost every programming language, including Python, Java, C++ and JavaScript.

Below image shows an example of a regular expression and explains its parts, helping you understand how filenames or patterns can be matched effectively.

example_of_regular_expression
Example of Regular Expression
This regex checks if a filename is valid, allowing letters, numbers, underscore, hyphens and ends with .jpg, .png or .gif. Example matches: file123.jpg, my-photo.png, logo_1.gif.

Examples: Match a Filename Ending with .jpg, .png, or .gif




#include <regex>
#include <iostream>
#include <string>
using namespace std;
​
int main() {
    regex pattern(R"(^[a-zA-Z0-9_-]+\.(jpg|png|gif)$)"); // Raw string literal for regex
    string filename = "file123.jpg";
    if (regex_match(filename, pattern)) {
        cout << "Valid image filename" << endl;
    } else {
        cout << "Invalid filename" << endl;
    }
    return 0;
}
Importance of Regular Expression
Efficient Pattern Matching: Quickly search for specific patterns in text or data without manual checking.
Data Validation: Validate inputs like email addresses, phone numbers, URLs, and passwords.
Text Manipulation: Perform search-and-replace operations across files or datasets effectively.
Automation in Analytics and Tools: Used in tools like Google Analytics for URL matching and filtering.
Cross-Platform Support: Works across programming languages and editors such as Python, Java, Sublime Text, Notepad++, and Microsoft Word.
Common Elements Used in Regular Expressions
Regular expressions are built using special symbols and characters. Below are the most commonly used regex elements explained with simple examples.

1. Repeaters (  *, +, and { } ): Repeaters specify how many times the preceding character or group should appear.

2. Asterisk symbol (*): Matches the preceding character 0 or more times.

Example: The regular expression ab*c will give ac, abc, abbc, abbbc….and so on 

3. The Plus symbol (+): Matches the preceding character 1 or more times.

Example: The regular expression ab+c will give abc, abbc, abbbc, … and so on.

4. The curly braces { … }: Defines an exact or range of repetitions.

Example: {{2}: exactly 2 times
                  {min,}: at least min times
                 {min,max}: between min and max times

5. Wildcard (.): Matches any single character except a newline.

Example: Regular expression .* will tell the computer that any character can be used any number of times.

6. Optional character (?): Matches 0 or 1 occurrence of the preceding character.

Example: docx? matches doc and docx

7. The caret ( ^ ) symbol: Ensures the match starts at the beginning of the string.

Example : ^\d{3} matches 901 in 901-333

8.  The dollar ( $ ) symbol: Ensures the match ends at the end of the string.

Example: \d{3}$ matches 333 in 901-333

9. Character Classes: Match specific types of characters: 

\s: whitespace
\S: non-whitespace
\d: digit
\D: non-digit
\w: word character (letters, digits, _)
\W: non-word character
\b: word boundary

Example: [abc] matches a, b, or c

10. Negated Character Class ([^ ]): Matches characters not listed in the brackets.

Example : [^abc] -> matches any character except a, b, c

okenization in NLP
Last Updated : 11 Jul, 2025
Tokenization is a fundamental step in Natural Language Processing (NLP). It involves dividing a Textual input into smaller units known as tokens. These tokens can be in the form of words, characters, sub-words, or sentences. It helps in improving interpretability of text by different models. Let's understand How Tokenization Works.

Tokenization-in-Natural-Language-Processing
Representation of Tokenization
What is Tokenization in NLP?
Natural Language Processing (NLP) is a subfield of Artificial Intelligence, information engineering, and human-computer interaction. It focuses on how to process and analyze large amounts of natural language data efficiently. It is difficult to perform as the process of reading and understanding languages is far more complex than it seems at first glance.

Tokenization is a foundation step in NLP pipeline that shapes the entire workflow.
Involves dividing a string or text into a list of smaller units known as tokens.
Uses a tokenizer to segment unstructured data and natural language text into distinct chunks of information, treating them as different elements.
Tokens: Words or Sub-words in the context of natural language processing. Example: A word is a token in a sentence, A character is a token in a word, etc.
Application: Multiple NLP tasks, text processing, language modelling, and machine translation.
Types of Tokenization
Types-of-Tokenization-in-NLP.webpTypes-of-Tokenization-in-NLP.webp
Tokenization can be classified into several types based on how the text is segmented. Here are some types of tokenization:

1. Word Tokenization
Word tokenization is the most commonly used method where text is divided into individual words. It works well for languages with clear word boundaries, like English. For example, "Machine learning is fascinating" becomes:

Input before tokenization: ["Machine Learning is fascinating"]

Output when tokenized by words: ["Machine", "learning", "is", "fascinating"]

2. Character Tokenization
In Character Tokenization, the textual data is split and converted to a sequence of individual characters. This is beneficial for tasks that require a detailed analysis, such as spelling correction or for tasks with unclear boundaries. It can also be useful for modelling character-level language.

Example

Input before tokenization: ["You are helpful"]

Output when tokenized by characters: ["Y", "o", "u", " ", "a", "r", "e", " ", "h", "e", "l", "p", "f", "u", "l"]

3. Sub-word Tokenization
This strikes a balance between word and character tokenization by breaking down text into units that are larger than a single character but smaller than a full word. This is useful when dealing with morphologically rich languages or rare words.

Example

["Time", "table"] 
["Rain", "coat"] 
["Grace", "fully"] 
["Run", "way"] 

Sub-word tokenization helps to handle out-of-vocabulary words in NLP tasks and for languages that form words by combining smaller units.

4. Sentence Tokenization
Sentence tokenization is also a common technique used to make a division of paragraphs or large set of sentences into separated sentences as tokens. This is useful for tasks requiring individual sentence analysis or processing.

Input before tokenization: ["Artificial Intelligence is an emerging technology. Machine learning is fascinating. Computer Vision handles images. "]

Output when tokenized by sentences ["Artificial Intelligence is an emerging technology.", "Machine learning is fascinating.", "Computer Vision handles images."]

5. N-gram Tokenization
N-gram tokenization splits words into fixed-sized chunks (size = n) of data.

Input before tokenization: ["Machine learning is powerful"]

Output when tokenized by bigrams: [('Machine', 'learning'), ('learning', 'is'), ('is', 'powerful')]

Need of Tokenization
Tokenization is an essential step in text processing and natural language processing (NLP) for several reasons. Some of these are listed below:

Effective Text Processing: Reduces the size of raw text, resulting in easy and efficient statistical and computational analysis.
Feature extraction: Text data can be represented numerically for algorithmic comprehension by using tokens as features in ML models.
Information Retrieval: Tokenization is essential for indexing and searching in systems that store and retrieve information efficiently based on words or phrases.
Text Analysis: Used in sentiment analysis and named entity recognition, to determine the function and context of individual words in a sentence.
Vocabulary Management: Generates a list of distinct tokens, Helps manage a corpus's vocabulary.
Task-Specific Adaptation: Adapts to need of particular NLP task, Good for summarization and machine translation.
Implementation for Tokenization
Sentence Tokenization using sent_tokenize
The code snippet uses sent_tokenize function from NLTK library. The sent_tokenize function is used to segment a given text into a list of sentences.


from nltk.tokenize import sent_tokenize

text = "Hello everyone. Welcome to GeeksforGeeks. You are studying NLP article."
sent_tokenize(text)
Output: 

['Hello everyone.',
 'Welcome to GeeksforGeeks.',
 'You are studying NLP article']

How sent_tokenize works: The sent_tokenize function uses an instance of PunktSentenceTokenizer from the nltk.tokenize.punkt module, which is already been trained and thus very well knows to mark the end and beginning of sentence at what characters and punctuation.

Sentence Tokenization using PunktSentenceTokenizer
It is efficient to use 'PunktSentenceTokenizer' to from the NLTK library. The Punkt tokenizer is a data-driven sentence tokenizer that comes with NLTK. It is trained on large corpus of text to identify sentence boundaries.


import nltk.data

# Loading PunktSentenceTokenizer using English pickle file
tokenizer = nltk.data.load('tokenizers/punkt/PY3/english.pickle')
tokenizer.tokenize(text)
Output: 

['Hello everyone.',
 'Welcome to GeeksforGeeks.',
 'You are studying NLP article']

Tokenize sentence of different language
Sentences from different languages can also be tokenized using different pickle file other than English. 

In the following code snippet, we have used NLTK library to tokenize a Spanish text into sentences using pre-trained Punkt tokenizer for Spanish.
The Punkt tokenizer: Data-driven ML-based tokenizer to identify sentence boundaries.

import nltk.data

spanish_tokenizer = nltk.data.load('tokenizers/punkt/PY3/spanish.pickle')

text = 'Hola amigo. Estoy bien.'
spanish_tokenizer.tokenize(text)
Output: 

['Hola amigo.', 
 'Estoy bien.']
Word Tokenization using work_tokenize
The code snipped uses the word_tokenize function from NLTK library to tokenize a given text into individual words.

The word_tokenize function is helpful for breaking down a sentence or text into its constituent words.
Eases analysis or processing at the word level in natural language processing tasks.

from nltk.tokenize import word_tokenize

text = "Hello everyone. Welcome to GeeksforGeeks."
word_tokenize(text)
Output: 

['Hello', 'everyone', '.', 'Welcome', 'to', 'GeeksforGeeks', '.']
How word_tokenize works: word_tokenize() function is a wrapper function that calls tokenize() on an instance of the TreebankWordTokenizer class.

Word Tokenization Using TreebankWordTokenizer 
The code snippet uses the TreebankWordTokenizer from the Natural Language Toolkit (NLTK) to tokenize a given text into individual words.


from nltk.tokenize import TreebankWordTokenizer

tokenizer = TreebankWordTokenizer()
tokenizer.tokenize(text)
Output:

['Hello', 'everyone.', 'Welcome', 'to', 'GeeksforGeeks', '.']
These tokenizers work by separating the words using punctuation and spaces. And as mentioned in the code outputs above, it doesn't discard the punctuation, allowing a user to decide what to do with the punctuations at the time of pre-processing.

Word Tokenization using WordPunctTokenizer
The WordPunctTokenizer is one of the NLTK tokenizers that splits words based on punctuation boundaries. Each punctuation mark is treated as a separate token.


from nltk.tokenize import WordPunctTokenizer

tokenizer = WordPunctTokenizer()
tokenizer.tokenize("Let's see how it's working.")
Output:

['Let', "'", 's', 'see', 'how', 'it', "'", 's', 'working', '.']

Word Tokenization using Regular Expression 
The code snippet uses the RegexpTokenizer from the Natural Language Toolkit (NLTK) to tokenize a given text based on a regular expression pattern.


from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')
text = "Let's see how it's working."
tokenizer.tokenize(text)
Output: 

['Let', 's', 'see', 'how', 'it', 's', 'working']
Using regular expressions allows for more fine-grained control over tokenization, and you can customize the pattern based on your specific requirements.

More Techniques for Tokenization
We have discussed the ways to implement how can we perform tokenization using NLTK library. We can also implement tokenization using following methods and libraries:

Spacy: Spacy is NLP library that provide robust tokenization capabilities.
BERT tokenizer: BERT uses Word Piece tokenizer, which is a type of sub-word tokenizer for tokenizing input text. Using regular expressions allows for more fine-grained control over tokenization, and you can customize the pattern based on your specific requirements.
Byte-Pair Encoding: Byte Pair Encoding (BPE) is a data compression algorithm that has also found applications in the field of natural language processing, specifically for tokenization. It is a Sub-word Tokenization technique that works by iteratively merging the most frequent pairs of consecutive bytes (or characters) in a given corpus.
Sentence Piece: Sentence Piece is another sub-word tokenization algorithm commonly used for natural language processing tasks. It is designed to be language-agnostic and works by iteratively merging frequent sequences of characters or sub words in a given corpus.
Limitations of Tokenization
Unable to capture the meaning of the sentence hence, results in ambiguity.
Chinese, Japanese, Arabic, lack distinct spaces between words. Hence, absence of clear boundaries that complicates the process of tokenization.
Tough to decide how to tokenize text that may include more than one word, for example email address, URLs and special symbols

Lemmatization with NLTK
Last Updated : 19 Jan, 2026
Lemmatization is an important text pre-processing technique in Natural Language Processing (NLP) that reduces words to their base form known as a "lemma." For example, the lemma of "running" is "run" and "better" becomes "good."

Unlike stemming which simply removes prefixes or suffixes, it considers the word's meaning and part of speech (POS) and ensures that the base form is a valid word. This makes lemmatization more accurate as it avoids generating non-dictionary words.

lemmatization
Lemmatization
It is used for:

Improves accuracy: It ensures words with similar meanings like "running" and "ran" are treated as the same.
Reduced Data Redundancy: By reducing words to their base forms, it reduces redundancy in the dataset. This leads to smaller datasets which makes it easier to handle and process large amounts of text for analysis or training machine learning models.
Better NLP Model Performance: By treating all similar word as same, it improves the performance of NLP models by making text more consistent. For example, treating "running," "ran" and "runs" as the same word improves the model's understanding of context and meaning.
Lemmatization Techniques
There are different techniques to perform lemmatization each with its own advantages and use cases:

1. Rule Based Lemmatization
In rule-based lemmatization, predefined rules are applied to a word to remove suffixes and get the root form. This approach works well for regular words but may not handle irregularities well.

For example:

Rule: For regular verbs ending in "-ed," remove the "-ed" suffix.

Example: "walked" -> "walk"

While this method is simple and interpretable, it doesn't account for irregular word forms like "better" which should be lemmatized to "good".

2. Dictionary-Based Lemmatization
It uses a predefined dictionary or lexicon such as WordNet to look up the base form of a word. This method is more accurate than rule-based lemmatization because it accounts for exceptions and irregular words.

For example:

'running' -> 'run'
'better' -> 'good'
'went' -> 'go
"I was running to become a better athlete and then I went home," -> "I was run to become a good athlete and then I go home."

By using dictionaries like WordNet this method can handle a range of words effectively, especially in languages with well-established dictionaries.

3. Machine Learning-Based Lemmatization
It uses algorithms trained on large datasets to automatically identify the base form of words. This approach is highly flexible and can handle irregular words and linguistic nuances better than the rule-based and dictionary-based methods.

For example:

A trained model may deduce that “went” corresponds to “go” even though the suffix removal rule doesn’t apply. Similarly, for 'happier' the model deduces 'happy' as the lemma. 

Machine learning-based lemmatizers are more adaptive and can generalize across different word forms which makes them ideal for complex tasks involving diverse vocabularies.

Implementation of Lemmatization in Python
Lets see step by step how Lemmatization works in Python:

Step 1: Installing NLTK and Downloading Necessary Resources
In Python, the NLTK library provides an easy and efficient way to implement lemmatization. First, we need to install the NLTK library and download the necessary datasets like WordNet and the punkt tokenizer.


!pip install nltk
Now lets import the library and download the necessary datasets.


import nltk
nltk.download('punkt_tab')      
nltk.download('wordnet')    
nltk.download('omw-1.4') 
nltk.download('averaged_perceptron_tagger_eng') 
Step 2: Lemmatizing Text with NLTK
Now we can tokenize the text and apply lemmatization using NLTK's WordNetLemmatizer.


from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
text = "The cats were running faster than the dogs."
tokens = word_tokenize(text)
lemmatized_words = [lemmatizer.lemmatize(word) for word in tokens]

print(f"Original Text: {text}")
print(f"Lemmatized Words: {lemmatized_words}")
Output: 

nltk1
Lemmatizing Text with NLTK
In this output, we can see that:

"cats" is reduced to its lemma "cat" (noun).
"running" remains "running" (since no POS tag is provided, NLTK doesn't convert it to "run").
Step 3: Improving Lemmatization with Part of Speech (POS) Tagging
To improve the accuracy of lemmatization, it’s important to specify the correct Part of Speech (POS) for each word. By default, NLTK assumes that words are nouns when no POS tag is provided. However, it can be more accurate if we specify the correct POS tag for each word.

For example:

"running" (as a verb) should be lemmatized to "run".
"better" (as an adjective) should be lemmatized to "good".

from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
sentence = "The children are running towards a better place."
tokens = word_tokenize(sentence)
tagged_tokens = pos_tag(tokens)


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return 'a'
    elif tag.startswith('V'):
        return 'v'
    elif tag.startswith('N'):
        return 'n'
    elif tag.startswith('R'):
        return 'r'
    else:
        return 'n'


lemmatized_sentence = []
for word, tag in tagged_tokens:
    if word.lower() == 'are' or word.lower() in ['is', 'am']:
        lemmatized_sentence.append(word)
    else:
        lemmatized_sentence.append(
            lemmatizer.lemmatize(word, get_wordnet_pos(tag)))
print("Original Sentence: ", sentence)
print("Lemmatized Sentence: ", ' '.join(lemmatized_sentence))
Output: 

nltk2
Improving Lemmatization with POS Tagging
In this improved version:

"children" is lemmatized to "child" (noun).
"running" is lemmatized to "run" (verb).
"better" is lemmatized to "good" (adjective).
Advantages
Lets see some key advantages:

Efficient Data Processing: It reduces the number of unique words by grouping similar variations together. This reduction helps to process large datasets more efficiently, conserving both memory and computational resources.
Enhanced Search and Retrieval: In tasks like search and information retrieval, it improves results by making it easier to match different forms of a word like "run," "running," "ran" to the same base form increasing the relevance of search queries.
Consistency in NLP Models: Standardizing words to their base form improves the consistency of input data which enhances the performance of NLP models. With consistent data, models are more likely to make accurate predictions and understand the underlying context of the text.
Disadvantages
Time-consuming: It can be slower compared to other techniques such as stemming because it involves parsing the text and performing dictionary lookups or morphological analysis.
Not Ideal for Real-Time Applications: Due to its time-consuming nature, it may not be well-suited for real-time applications where fast processing is important.
Risk of Ambiguity: It may sometimes produce ambiguous results, when a word has multiple meanings based on its context. For example, the word "lead" can refer to both the noun (a type of metal) and a verb (to guide). Without context, the lemmatizer might not always resolve these ambiguities correctly.

Introduction to Stemming
Last Updated : 17 Dec, 2025
Stemming is an important text-processing technique that reduces words to their base or root form by removing prefixes and suffixes. This process standardizes words which helps to improve the efficiency and effectiveness of various natural language processing (NLP) tasks.

popular_stemming_algorithms.webppopular_stemming_algorithms.webp
In NLP, stemming simplifies words to their most basic form, making it easier to analyze and process text. For example, "chocolates" becomes "chocolate" and "retrieval" becomes "retrieve". This is important in the early stages of NLP tasks where words are extracted from a document and tokenized (broken into individual words).

It helps in tasks such as text classification, information retrieval and text summarization by reducing words to a base form. While it is effective, it can sometimes introduce drawbacks including potential inaccuracies and a reduction in text readability.

Examples of stemming for the word "like":

"likes" → "like"
"liked" → "like"
"likely" → "like"
"liking" → "like"
Types of Stemmer in NLTK 
Python's NLTK (Natural Language Toolkit) provides various stemming algorithms each suitable for different scenarios and languages. Lets see an overview of some of the most commonly used stemmers:

1. Porter's Stemmer
Porter's Stemmer is one of the most popular and widely used stemming algorithms. Proposed in 1980 by Martin Porter, this stemmer works by applying a series of rules to remove common suffixes from English words. It is well-known for its simplicity, speed and reliability. However, the stemmed output is not guaranteed to be a meaningful word and its applications are limited to the English language.

Example:

'agreed' → 'agree'
Rule: If the word has a suffix EED (with at least one vowel and consonant) remove the suffix and change it to EE.
Advantages:

Very fast and efficient.
Commonly used for tasks like information retrieval and text mining.
Limitations:

Outputs may not always be real words.
Limited to English words.
Now lets implement Porter's Stemmer in Python, here we will be using NLTK library.


from nltk.stem import PorterStemmer

porter_stemmer = PorterStemmer()

words = ["running", "jumps", "happily", "running", "happily"]

stemmed_words = [porter_stemmer.stem(word) for word in words]

print("Original words:", words)
print("Stemmed words:", stemmed_words)
Output:

stem1
Porter's Stemmer
2. Snowball Stemmer
The Snowball Stemmer is an enhanced version of the Porter Stemmer which was introduced by Martin Porter as well. It is referred to as Porter2 and is faster and more aggressive than its predecessor. One of the key advantages of this is that it supports multiple languages, making it a multilingual stemmer.

Example:

'running' → 'run'
'quickly' → 'quick'
Advantages:

More efficient than Porter Stemmer.
Supports multiple languages.
Limitations:

More aggressive which might lead to over-stemming.
Now lets implement Snowball Stemmer in Python, here we will be using NLTK library.




from nltk.stem import SnowballStemmer
​
stemmer = SnowballStemmer(language='english')
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem2
Snowball Stemmer
3. Lancaster Stemmer
The Lancaster Stemmer is known for being more aggressive and faster than other stemmers. However, it’s also more destructive and may lead to excessively shortened stems. It uses a set of external rules that are applied in an iterative manner.

Example:

'running' → 'run'
'happily' → 'happy'
Advantages:

Very fast.
Good for smaller datasets or quick preprocessing.
Limitations:

Aggressive which can result in over-stemming.
Less efficient than Snowball in larger datasets.
Now lets implement Lancaster Stemmer in Python, here we will be using NLTK library.




from nltk.stem import LancasterStemmer
​
stemmer = LancasterStemmer()
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem3
Lancaster Stemmer
4. Regexp Stemmer
The Regexp Stemmer or Regular Expression Stemmer is a flexible stemming algorithm that allows users to define custom rules using regular expressions (regex). This stemmer can be helpful for very specific tasks where predefined rules are necessary for stemming.

Example:

'running' → 'runn'
Custom rule: r'ing$' removes the suffix ing.
Advantages:

Highly customizable using regular expressions.
Suitable for domain-specific tasks.
Limitations:

Requires manual rule definition.
Can be computationally expensive for large datasets.
Now let's implement Regexp Stemmer in Python, here we will be using NLTK library.




from nltk.stem import RegexpStemmer
​
custom_rule = r'ing$'
regexp_stemmer = RegexpStemmer(custom_rule)
​
word = 'running'
stemmed_word = regexp_stemmer.stem(word)
​
print(f'Original Word: {word}')
print(f'Stemmed Word: {stemmed_word}')
Output:

stem4
Regexp Stemmer
5. Krovetz Stemmer 
The Krovetz Stemmer was developed by Robert Krovetz in 1993. It is designed to be more linguistically accurate and tends to preserve meaning more effectively than other stemmers. It includes steps like converting plural forms to singular and removing ing from past-tense verbs.

Example:

'children' → 'child'
'running' → 'run'
Advantages:

More accurate, as it preserves linguistic meaning.
Works well with both singular/plural and past/present tense conversions.
Limitations:

May be inefficient with large corpora.
Slower compared to other stemmers.
Note: The Krovetz Stemmer is not natively available in the NLTK library, unlike other stemmers such as Porter, Snowball or Lancaster.

Stemming vs. Lemmatization
Let's see the tabular difference between Stemming and Lemmatization for better understanding:

Stemming	Lemmatization
Reduces words to their root form often resulting in non-valid words.	Reduces words to their base form (lemma) ensuring a valid word.
Based on simple rules or algorithms.	Considers the word's meaning and context to return the base form.
May not always produce a valid word.	Always produces a valid word.
Example: "Better" → "bet"	Example: "Better" → "good"
No context is considered.	Considers the context and part of speech.
Applications of Stemming
Stemming plays an important role in many NLP tasks. Some of its key applications include:

Information Retrieval: It is used in search engines to improve the accuracy of search results. By reducing words to their root form, it ensures that documents with different word forms like "run," "running," "runner" are grouped together.
Text Classification: In text classification, it helps in reducing the feature space by consolidating variations of words into a single representation. This can improve the performance of machine learning algorithms.
Document Clustering: It helps in grouping similar documents by normalizing word forms, making it easier to identify patterns across large text corpora.
Sentiment Analysis: Before sentiment analysis, it is used to process reviews and comments. This allows the system to analyze sentiments based on root words which improves its ability to understand positive or negative sentiments despite word variations.
Challenges in Stemming
While stemming is beneficial but also it has some challenges:

Over-Stemming: When words are reduced too aggressively, leading to the loss of meaning. For example, "arguing" becomes "argu" making it harder to understand.
Under-Stemming: Occurs when related words are not reduced to a common base form, causing inconsistencies. For example, "argument" and "arguing" might not be stemmed similarly.
Loss of Meaning: Stemming ignores context which can result in incorrect interpretations in tasks like sentiment analysis.
Choosing the Right Stemmer: Different stemmers may produce diffierent results which requires careful selection and testing for the best fit.
These challenges can be solved by fine-tuning the stemming process or using lemmatization when necessary.

Advantages of Stemming
Stemming provides various benefits which are as follows:

Text Normalization: By reducing words to their root form, it helps to normalize text which makes it easier to analyze and process.
Improved Efficiency: It reduces the dimensionality of text data which can improve the performance of machine learning algorithms.
Information Retrieval: It enhances search engine performance by ensuring that variations of the same word are treated as the same entity.
Facilitates Language Processing: It simplifies the text by reducing variations of words which makes it easier to process and analyze large text datasets.
Related Articles:
Tokenization

Introduction to Stemming
Last Updated : 17 Dec, 2025
Stemming is an important text-processing technique that reduces words to their base or root form by removing prefixes and suffixes. This process standardizes words which helps to improve the efficiency and effectiveness of various natural language processing (NLP) tasks.

popular_stemming_algorithms.webppopular_stemming_algorithms.webp
In NLP, stemming simplifies words to their most basic form, making it easier to analyze and process text. For example, "chocolates" becomes "chocolate" and "retrieval" becomes "retrieve". This is important in the early stages of NLP tasks where words are extracted from a document and tokenized (broken into individual words).

It helps in tasks such as text classification, information retrieval and text summarization by reducing words to a base form. While it is effective, it can sometimes introduce drawbacks including potential inaccuracies and a reduction in text readability.

Examples of stemming for the word "like":

"likes" → "like"
"liked" → "like"
"likely" → "like"
"liking" → "like"
Types of Stemmer in NLTK 
Python's NLTK (Natural Language Toolkit) provides various stemming algorithms each suitable for different scenarios and languages. Lets see an overview of some of the most commonly used stemmers:

1. Porter's Stemmer
Porter's Stemmer is one of the most popular and widely used stemming algorithms. Proposed in 1980 by Martin Porter, this stemmer works by applying a series of rules to remove common suffixes from English words. It is well-known for its simplicity, speed and reliability. However, the stemmed output is not guaranteed to be a meaningful word and its applications are limited to the English language.

Example:

'agreed' → 'agree'
Rule: If the word has a suffix EED (with at least one vowel and consonant) remove the suffix and change it to EE.
Advantages:

Very fast and efficient.
Commonly used for tasks like information retrieval and text mining.
Limitations:

Outputs may not always be real words.
Limited to English words.
Now lets implement Porter's Stemmer in Python, here we will be using NLTK library.


from nltk.stem import PorterStemmer

porter_stemmer = PorterStemmer()

words = ["running", "jumps", "happily", "running", "happily"]

stemmed_words = [porter_stemmer.stem(word) for word in words]

print("Original words:", words)
print("Stemmed words:", stemmed_words)
Output:

stem1
Porter's Stemmer
2. Snowball Stemmer
The Snowball Stemmer is an enhanced version of the Porter Stemmer which was introduced by Martin Porter as well. It is referred to as Porter2 and is faster and more aggressive than its predecessor. One of the key advantages of this is that it supports multiple languages, making it a multilingual stemmer.

Example:

'running' → 'run'
'quickly' → 'quick'
Advantages:

More efficient than Porter Stemmer.
Supports multiple languages.
Limitations:

More aggressive which might lead to over-stemming.
Now lets implement Snowball Stemmer in Python, here we will be using NLTK library.




from nltk.stem import SnowballStemmer
​
stemmer = SnowballStemmer(language='english')
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem2
Snowball Stemmer
3. Lancaster Stemmer
The Lancaster Stemmer is known for being more aggressive and faster than other stemmers. However, it’s also more destructive and may lead to excessively shortened stems. It uses a set of external rules that are applied in an iterative manner.

Example:

'running' → 'run'
'happily' → 'happy'
Advantages:

Very fast.
Good for smaller datasets or quick preprocessing.
Limitations:

Aggressive which can result in over-stemming.
Less efficient than Snowball in larger datasets.
Now lets implement Lancaster Stemmer in Python, here we will be using NLTK library.




from nltk.stem import LancasterStemmer
​
stemmer = LancasterStemmer()
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem3
Lancaster Stemmer
4. Regexp Stemmer
The Regexp Stemmer or Regular Expression Stemmer is a flexible stemming algorithm that allows users to define custom rules using regular expressions (regex). This stemmer can be helpful for very specific tasks where predefined rules are necessary for stemming.

Example:

'running' → 'runn'
Custom rule: r'ing$' removes the suffix ing.
Advantages:

Highly customizable using regular expressions.
Suitable for domain-specific tasks.
Limitations:

Requires manual rule definition.
Can be computationally expensive for large datasets.
Now let's implement Regexp Stemmer in Python, here we will be using NLTK library.




from nltk.stem import RegexpStemmer
​
custom_rule = r'ing$'
regexp_stemmer = RegexpStemmer(custom_rule)
​
word = 'running'
stemmed_word = regexp_stemmer.stem(word)
​
print(f'Original Word: {word}')
print(f'Stemmed Word: {stemmed_word}')
Output:

stem4
Regexp Stemmer
5. Krovetz Stemmer 
The Krovetz Stemmer was developed by Robert Krovetz in 1993. It is designed to be more linguistically accurate and tends to preserve meaning more effectively than other stemmers. It includes steps like converting plural forms to singular and removing ing from past-tense verbs.

Example:

'children' → 'child'
'running' → 'run'
Advantages:

More accurate, as it preserves linguistic meaning.
Works well with both singular/plural and past/present tense conversions.
Limitations:

May be inefficient with large corpora.
Slower compared to other stemmers.
Note: The Krovetz Stemmer is not natively available in the NLTK library, unlike other stemmers such as Porter, Snowball or Lancaster.

Stemming vs. Lemmatization
Let's see the tabular difference between Stemming and Lemmatization for better understanding:

Stemming	Lemmatization
Reduces words to their root form often resulting in non-valid words.	Reduces words to their base form (lemma) ensuring a valid word.
Based on simple rules or algorithms.	Considers the word's meaning and context to return the base form.
May not always produce a valid word.	Always produces a valid word.
Example: "Better" → "bet"	Example: "Better" → "good"
No context is considered.	Considers the context and part of speech.
Applications of Stemming
Stemming plays an important role in many NLP tasks. Some of its key applications include:

Information Retrieval: It is used in search engines to improve the accuracy of search results. By reducing words to their root form, it ensures that documents with different word forms like "run," "running," "runner" are grouped together.
Text Classification: In text classification, it helps in reducing the feature space by consolidating variations of words into a single representation. This can improve the performance of machine learning algorithms.
Document Clustering: It helps in grouping similar documents by normalizing word forms, making it easier to identify patterns across large text corpora.
Sentiment Analysis: Before sentiment analysis, it is used to process reviews and comments. This allows the system to analyze sentiments based on root words which improves its ability to understand positive or negative sentiments despite word variations.
Challenges in Stemming
While stemming is beneficial but also it has some challenges:

Over-Stemming: When words are reduced too aggressively, leading to the loss of meaning. For example, "arguing" becomes "argu" making it harder to understand.
Under-Stemming: Occurs when related words are not reduced to a common base form, causing inconsistencies. For example, "argument" and "arguing" might not be stemmed similarly.
Loss of Meaning: Stemming ignores context which can result in incorrect interpretations in tasks like sentiment analysis.
Choosing the Right Stemmer: Different stemmers may produce diffierent results which requires careful selection and testing for the best fit.
These challenges can be solved by fine-tuning the stemming process or using lemmatization when necessary.

Advantages of Stemming
Stemming provides various benefits which are as follows:

Text Normalization: By reducing words to their root form, it helps to normalize text which makes it easier to analyze and process.
Improved Efficiency: It reduces the dimensionality of text data which can improve the performance of machine learning algorithms.
Information Retrieval: It enhances search engine performance by ensuring that variations of the same word are treated as the same entity.
Facilitates Language Processing: It simplifies the text by reducing variations of words which makes it easier to process and analyze large text datasets.
Related Articles:
Tokenization

Introduction to Stemming
Last Updated : 17 Dec, 2025
Stemming is an important text-processing technique that reduces words to their base or root form by removing prefixes and suffixes. This process standardizes words which helps to improve the efficiency and effectiveness of various natural language processing (NLP) tasks.

popular_stemming_algorithms.webppopular_stemming_algorithms.webp
In NLP, stemming simplifies words to their most basic form, making it easier to analyze and process text. For example, "chocolates" becomes "chocolate" and "retrieval" becomes "retrieve". This is important in the early stages of NLP tasks where words are extracted from a document and tokenized (broken into individual words).

It helps in tasks such as text classification, information retrieval and text summarization by reducing words to a base form. While it is effective, it can sometimes introduce drawbacks including potential inaccuracies and a reduction in text readability.

Examples of stemming for the word "like":

"likes" → "like"
"liked" → "like"
"likely" → "like"
"liking" → "like"
Types of Stemmer in NLTK 
Python's NLTK (Natural Language Toolkit) provides various stemming algorithms each suitable for different scenarios and languages. Lets see an overview of some of the most commonly used stemmers:

1. Porter's Stemmer
Porter's Stemmer is one of the most popular and widely used stemming algorithms. Proposed in 1980 by Martin Porter, this stemmer works by applying a series of rules to remove common suffixes from English words. It is well-known for its simplicity, speed and reliability. However, the stemmed output is not guaranteed to be a meaningful word and its applications are limited to the English language.

Example:

'agreed' → 'agree'
Rule: If the word has a suffix EED (with at least one vowel and consonant) remove the suffix and change it to EE.
Advantages:

Very fast and efficient.
Commonly used for tasks like information retrieval and text mining.
Limitations:

Outputs may not always be real words.
Limited to English words.
Now lets implement Porter's Stemmer in Python, here we will be using NLTK library.


from nltk.stem import PorterStemmer

porter_stemmer = PorterStemmer()

words = ["running", "jumps", "happily", "running", "happily"]

stemmed_words = [porter_stemmer.stem(word) for word in words]

print("Original words:", words)
print("Stemmed words:", stemmed_words)
Output:

stem1
Porter's Stemmer
2. Snowball Stemmer
The Snowball Stemmer is an enhanced version of the Porter Stemmer which was introduced by Martin Porter as well. It is referred to as Porter2 and is faster and more aggressive than its predecessor. One of the key advantages of this is that it supports multiple languages, making it a multilingual stemmer.

Example:

'running' → 'run'
'quickly' → 'quick'
Advantages:

More efficient than Porter Stemmer.
Supports multiple languages.
Limitations:

More aggressive which might lead to over-stemming.
Now lets implement Snowball Stemmer in Python, here we will be using NLTK library.




from nltk.stem import SnowballStemmer
​
stemmer = SnowballStemmer(language='english')
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem2
Snowball Stemmer
3. Lancaster Stemmer
The Lancaster Stemmer is known for being more aggressive and faster than other stemmers. However, it’s also more destructive and may lead to excessively shortened stems. It uses a set of external rules that are applied in an iterative manner.

Example:

'running' → 'run'
'happily' → 'happy'
Advantages:

Very fast.
Good for smaller datasets or quick preprocessing.
Limitations:

Aggressive which can result in over-stemming.
Less efficient than Snowball in larger datasets.
Now lets implement Lancaster Stemmer in Python, here we will be using NLTK library.




from nltk.stem import LancasterStemmer
​
stemmer = LancasterStemmer()
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem3
Lancaster Stemmer
4. Regexp Stemmer
The Regexp Stemmer or Regular Expression Stemmer is a flexible stemming algorithm that allows users to define custom rules using regular expressions (regex). This stemmer can be helpful for very specific tasks where predefined rules are necessary for stemming.

Example:

'running' → 'runn'
Custom rule: r'ing$' removes the suffix ing.
Advantages:

Highly customizable using regular expressions.
Suitable for domain-specific tasks.
Limitations:

Requires manual rule definition.
Can be computationally expensive for large datasets.
Now let's implement Regexp Stemmer in Python, here we will be using NLTK library.




from nltk.stem import RegexpStemmer
​
custom_rule = r'ing$'
regexp_stemmer = RegexpStemmer(custom_rule)
​
word = 'running'
stemmed_word = regexp_stemmer.stem(word)
​
print(f'Original Word: {word}')
print(f'Stemmed Word: {stemmed_word}')
Output:

stem4
Regexp Stemmer
5. Krovetz Stemmer 
The Krovetz Stemmer was developed by Robert Krovetz in 1993. It is designed to be more linguistically accurate and tends to preserve meaning more effectively than other stemmers. It includes steps like converting plural forms to singular and removing ing from past-tense verbs.

Example:

'children' → 'child'
'running' → 'run'
Advantages:

More accurate, as it preserves linguistic meaning.
Works well with both singular/plural and past/present tense conversions.
Limitations:

May be inefficient with large corpora.
Slower compared to other stemmers.
Note: The Krovetz Stemmer is not natively available in the NLTK library, unlike other stemmers such as Porter, Snowball or Lancaster.

Stemming vs. Lemmatization
Let's see the tabular difference between Stemming and Lemmatization for better understanding:

Stemming	Lemmatization
Reduces words to their root form often resulting in non-valid words.	Reduces words to their base form (lemma) ensuring a valid word.
Based on simple rules or algorithms.	Considers the word's meaning and context to return the base form.
May not always produce a valid word.	Always produces a valid word.
Example: "Better" → "bet"	Example: "Better" → "good"
No context is considered.	Considers the context and part of speech.
Applications of Stemming
Stemming plays an important role in many NLP tasks. Some of its key applications include:

Information Retrieval: It is used in search engines to improve the accuracy of search results. By reducing words to their root form, it ensures that documents with different word forms like "run," "running," "runner" are grouped together.
Text Classification: In text classification, it helps in reducing the feature space by consolidating variations of words into a single representation. This can improve the performance of machine learning algorithms.
Document Clustering: It helps in grouping similar documents by normalizing word forms, making it easier to identify patterns across large text corpora.
Sentiment Analysis: Before sentiment analysis, it is used to process reviews and comments. This allows the system to analyze sentiments based on root words which improves its ability to understand positive or negative sentiments despite word variations.
Challenges in Stemming
While stemming is beneficial but also it has some challenges:

Over-Stemming: When words are reduced too aggressively, leading to the loss of meaning. For example, "arguing" becomes "argu" making it harder to understand.
Under-Stemming: Occurs when related words are not reduced to a common base form, causing inconsistencies. For example, "argument" and "arguing" might not be stemmed similarly.
Loss of Meaning: Stemming ignores context which can result in incorrect interpretations in tasks like sentiment analysis.
Choosing the Right Stemmer: Different stemmers may produce diffierent results which requires careful selection and testing for the best fit.
These challenges can be solved by fine-tuning the stemming process or using lemmatization when necessary.

Advantages of Stemming
Stemming provides various benefits which are as follows:

Text Normalization: By reducing words to their root form, it helps to normalize text which makes it easier to analyze and process.
Improved Efficiency: It reduces the dimensionality of text data which can improve the performance of machine learning algorithms.
Information Retrieval: It enhances search engine performance by ensuring that variations of the same word are treated as the same entity.
Facilitates Language Processing: It simplifies the text by reducing variations of words which makes it easier to process and analyze large text datasets.
Related Articles:
TokenizationIntroduction to Stemming
Last Updated : 17 Dec, 2025
Stemming is an important text-processing technique that reduces words to their base or root form by removing prefixes and suffixes. This process standardizes words which helps to improve the efficiency and effectiveness of various natural language processing (NLP) tasks.

popular_stemming_algorithms.webppopular_stemming_algorithms.webp
In NLP, stemming simplifies words to their most basic form, making it easier to analyze and process text. For example, "chocolates" becomes "chocolate" and "retrieval" becomes "retrieve". This is important in the early stages of NLP tasks where words are extracted from a document and tokenized (broken into individual words).

It helps in tasks such as text classification, information retrieval and text summarization by reducing words to a base form. While it is effective, it can sometimes introduce drawbacks including potential inaccuracies and a reduction in text readability.

Examples of stemming for the word "like":

"likes" → "like"
"liked" → "like"
"likely" → "like"
"liking" → "like"
Types of Stemmer in NLTK 
Python's NLTK (Natural Language Toolkit) provides various stemming algorithms each suitable for different scenarios and languages. Lets see an overview of some of the most commonly used stemmers:

1. Porter's Stemmer
Porter's Stemmer is one of the most popular and widely used stemming algorithms. Proposed in 1980 by Martin Porter, this stemmer works by applying a series of rules to remove common suffixes from English words. It is well-known for its simplicity, speed and reliability. However, the stemmed output is not guaranteed to be a meaningful word and its applications are limited to the English language.

Example:

'agreed' → 'agree'
Rule: If the word has a suffix EED (with at least one vowel and consonant) remove the suffix and change it to EE.
Advantages:

Very fast and efficient.
Commonly used for tasks like information retrieval and text mining.
Limitations:

Outputs may not always be real words.
Limited to English words.
Now lets implement Porter's Stemmer in Python, here we will be using NLTK library.


from nltk.stem import PorterStemmer

porter_stemmer = PorterStemmer()

words = ["running", "jumps", "happily", "running", "happily"]

stemmed_words = [porter_stemmer.stem(word) for word in words]

print("Original words:", words)
print("Stemmed words:", stemmed_words)
Output:

stem1
Porter's Stemmer
2. Snowball Stemmer
The Snowball Stemmer is an enhanced version of the Porter Stemmer which was introduced by Martin Porter as well. It is referred to as Porter2 and is faster and more aggressive than its predecessor. One of the key advantages of this is that it supports multiple languages, making it a multilingual stemmer.

Example:

'running' → 'run'
'quickly' → 'quick'
Advantages:

More efficient than Porter Stemmer.
Supports multiple languages.
Limitations:

More aggressive which might lead to over-stemming.
Now lets implement Snowball Stemmer in Python, here we will be using NLTK library.




from nltk.stem import SnowballStemmer
​
stemmer = SnowballStemmer(language='english')
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem2
Snowball Stemmer
3. Lancaster Stemmer
The Lancaster Stemmer is known for being more aggressive and faster than other stemmers. However, it’s also more destructive and may lead to excessively shortened stems. It uses a set of external rules that are applied in an iterative manner.

Example:

'running' → 'run'
'happily' → 'happy'
Advantages:

Very fast.
Good for smaller datasets or quick preprocessing.
Limitations:

Aggressive which can result in over-stemming.
Less efficient than Snowball in larger datasets.
Now lets implement Lancaster Stemmer in Python, here we will be using NLTK library.




from nltk.stem import LancasterStemmer
​
stemmer = LancasterStemmer()
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem3
Lancaster Stemmer
4. Regexp Stemmer
The Regexp Stemmer or Regular Expression Stemmer is a flexible stemming algorithm that allows users to define custom rules using regular expressions (regex). This stemmer can be helpful for very specific tasks where predefined rules are necessary for stemming.

Example:

'running' → 'runn'
Custom rule: r'ing$' removes the suffix ing.
Advantages:

Highly customizable using regular expressions.
Suitable for domain-specific tasks.
Limitations:

Requires manual rule definition.
Can be computationally expensive for large datasets.
Now let's implement Regexp Stemmer in Python, here we will be using NLTK library.




from nltk.stem import RegexpStemmer
​
custom_rule = r'ing$'
regexp_stemmer = RegexpStemmer(custom_rule)
​
word = 'running'
stemmed_word = regexp_stemmer.stem(word)
​
print(f'Original Word: {word}')
print(f'Stemmed Word: {stemmed_word}')
Output:

stem4
Regexp Stemmer
5. Krovetz Stemmer 
The Krovetz Stemmer was developed by Robert Krovetz in 1993. It is designed to be more linguistically accurate and tends to preserve meaning more effectively than other stemmers. It includes steps like converting plural forms to singular and removing ing from past-tense verbs.

Example:

'children' → 'child'
'running' → 'run'
Advantages:

More accurate, as it preserves linguistic meaning.
Works well with both singular/plural and past/present tense conversions.
Limitations:

May be inefficient with large corpora.
Slower compared to other stemmers.
Note: The Krovetz Stemmer is not natively available in the NLTK library, unlike other stemmers such as Porter, Snowball or Lancaster.

Stemming vs. Lemmatization
Let's see the tabular difference between Stemming and Lemmatization for better understanding:

Stemming	Lemmatization
Reduces words to their root form often resulting in non-valid words.	Reduces words to their base form (lemma) ensuring a valid word.
Based on simple rules or algorithms.	Considers the word's meaning and context to return the base form.
May not always produce a valid word.	Always produces a valid word.
Example: "Better" → "bet"	Example: "Better" → "good"
No context is considered.	Considers the context and part of speech.
Applications of Stemming
Stemming plays an important role in many NLP tasks. Some of its key applications include:

Information Retrieval: It is used in search engines to improve the accuracy of search results. By reducing words to their root form, it ensures that documents with different word forms like "run," "running," "runner" are grouped together.
Text Classification: In text classification, it helps in reducing the feature space by consolidating variations of words into a single representation. This can improve the performance of machine learning algorithms.
Document Clustering: It helps in grouping similar documents by normalizing word forms, making it easier to identify patterns across large text corpora.
Sentiment Analysis: Before sentiment analysis, it is used to process reviews and comments. This allows the system to analyze sentiments based on root words which improves its ability to understand positive or negative sentiments despite word variations.
Challenges in Stemming
While stemming is beneficial but also it has some challenges:

Over-Stemming: When words are reduced too aggressively, leading to the loss of meaning. For example, "arguing" becomes "argu" making it harder to understand.
Under-Stemming: Occurs when related words are not reduced to a common base form, causing inconsistencies. For example, "argument" and "arguing" might not be stemmed similarly.
Loss of Meaning: Stemming ignores context which can result in incorrect interpretations in tasks like sentiment analysis.
Choosing the Right Stemmer: Different stemmers may produce diffierent results which requires careful selection and testing for the best fit.
These challenges can be solved by fine-tuning the stemming process or using lemmatization when necessary.

Advantages of Stemming
Stemming provides various benefits which are as follows:

Text Normalization: By reducing words to their root form, it helps to normalize text which makes it easier to analyze and process.
Improved Efficiency: It reduces the dimensionality of text data which can improve the performance of machine learning algorithms.
Information Retrieval: It enhances search engine performance by ensuring that variations of the same word are treated as the same entity.
Facilitates Language Processing: It simplifies the text by reducing variations of words which makes it easier to process and analyze large text datasets.
Related Articles:
TokenizationIntroduction to Stemming
Last Updated : 17 Dec, 2025
Stemming is an important text-processing technique that reduces words to their base or root form by removing prefixes and suffixes. This process standardizes words which helps to improve the efficiency and effectiveness of various natural language processing (NLP) tasks.

popular_stemming_algorithms.webppopular_stemming_algorithms.webp
In NLP, stemming simplifies words to their most basic form, making it easier to analyze and process text. For example, "chocolates" becomes "chocolate" and "retrieval" becomes "retrieve". This is important in the early stages of NLP tasks where words are extracted from a document and tokenized (broken into individual words).

It helps in tasks such as text classification, information retrieval and text summarization by reducing words to a base form. While it is effective, it can sometimes introduce drawbacks including potential inaccuracies and a reduction in text readability.

Examples of stemming for the word "like":

"likes" → "like"
"liked" → "like"
"likely" → "like"
"liking" → "like"
Types of Stemmer in NLTK 
Python's NLTK (Natural Language Toolkit) provides various stemming algorithms each suitable for different scenarios and languages. Lets see an overview of some of the most commonly used stemmers:

1. Porter's Stemmer
Porter's Stemmer is one of the most popular and widely used stemming algorithms. Proposed in 1980 by Martin Porter, this stemmer works by applying a series of rules to remove common suffixes from English words. It is well-known for its simplicity, speed and reliability. However, the stemmed output is not guaranteed to be a meaningful word and its applications are limited to the English language.

Example:

'agreed' → 'agree'
Rule: If the word has a suffix EED (with at least one vowel and consonant) remove the suffix and change it to EE.
Advantages:

Very fast and efficient.
Commonly used for tasks like information retrieval and text mining.
Limitations:

Outputs may not always be real words.
Limited to English words.
Now lets implement Porter's Stemmer in Python, here we will be using NLTK library.


from nltk.stem import PorterStemmer

porter_stemmer = PorterStemmer()

words = ["running", "jumps", "happily", "running", "happily"]

stemmed_words = [porter_stemmer.stem(word) for word in words]

print("Original words:", words)
print("Stemmed words:", stemmed_words)
Output:

stem1
Porter's Stemmer
2. Snowball Stemmer
The Snowball Stemmer is an enhanced version of the Porter Stemmer which was introduced by Martin Porter as well. It is referred to as Porter2 and is faster and more aggressive than its predecessor. One of the key advantages of this is that it supports multiple languages, making it a multilingual stemmer.

Example:

'running' → 'run'
'quickly' → 'quick'
Advantages:

More efficient than Porter Stemmer.
Supports multiple languages.
Limitations:

More aggressive which might lead to over-stemming.
Now lets implement Snowball Stemmer in Python, here we will be using NLTK library.




from nltk.stem import SnowballStemmer
​
stemmer = SnowballStemmer(language='english')
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem2
Snowball Stemmer
3. Lancaster Stemmer
The Lancaster Stemmer is known for being more aggressive and faster than other stemmers. However, it’s also more destructive and may lead to excessively shortened stems. It uses a set of external rules that are applied in an iterative manner.

Example:

'running' → 'run'
'happily' → 'happy'
Advantages:

Very fast.
Good for smaller datasets or quick preprocessing.
Limitations:

Aggressive which can result in over-stemming.
Less efficient than Snowball in larger datasets.
Now lets implement Lancaster Stemmer in Python, here we will be using NLTK library.




from nltk.stem import LancasterStemmer
​
stemmer = LancasterStemmer()
​
words_to_stem = ['running', 'jumped', 'happily', 'quickly', 'foxes']
​
stemmed_words = [stemmer.stem(word) for word in words_to_stem]
​
print("Original words:", words_to_stem)
print("Stemmed words:", stemmed_words)
Output:

stem3
Lancaster Stemmer
4. Regexp Stemmer
The Regexp Stemmer or Regular Expression Stemmer is a flexible stemming algorithm that allows users to define custom rules using regular expressions (regex). This stemmer can be helpful for very specific tasks where predefined rules are necessary for stemming.

Example:

'running' → 'runn'
Custom rule: r'ing$' removes the suffix ing.
Advantages:

Highly customizable using regular expressions.
Suitable for domain-specific tasks.
Limitations:

Requires manual rule definition.
Can be computationally expensive for large datasets.
Now let's implement Regexp Stemmer in Python, here we will be using NLTK library.




from nltk.stem import RegexpStemmer
​
custom_rule = r'ing$'
regexp_stemmer = RegexpStemmer(custom_rule)
​
word = 'running'
stemmed_word = regexp_stemmer.stem(word)
​
print(f'Original Word: {word}')
print(f'Stemmed Word: {stemmed_word}')
Output:

stem4
Regexp Stemmer
5. Krovetz Stemmer 
The Krovetz Stemmer was developed by Robert Krovetz in 1993. It is designed to be more linguistically accurate and tends to preserve meaning more effectively than other stemmers. It includes steps like converting plural forms to singular and removing ing from past-tense verbs.

Example:

'children' → 'child'
'running' → 'run'
Advantages:

More accurate, as it preserves linguistic meaning.
Works well with both singular/plural and past/present tense conversions.
Limitations:

May be inefficient with large corpora.
Slower compared to other stemmers.
Note: The Krovetz Stemmer is not natively available in the NLTK library, unlike other stemmers such as Porter, Snowball or Lancaster.

Stemming vs. Lemmatization
Let's see the tabular difference between Stemming and Lemmatization for better understanding:

Stemming	Lemmatization
Reduces words to their root form often resulting in non-valid words.	Reduces words to their base form (lemma) ensuring a valid word.
Based on simple rules or algorithms.	Considers the word's meaning and context to return the base form.
May not always produce a valid word.	Always produces a valid word.
Example: "Better" → "bet"	Example: "Better" → "good"
No context is considered.	Considers the context and part of speech.
Applications of Stemming
Stemming plays an important role in many NLP tasks. Some of its key applications include:

Information Retrieval: It is used in search engines to improve the accuracy of search results. By reducing words to their root form, it ensures that documents with different word forms like "run," "running," "runner" are grouped together.
Text Classification: In text classification, it helps in reducing the feature space by consolidating variations of words into a single representation. This can improve the performance of machine learning algorithms.
Document Clustering: It helps in grouping similar documents by normalizing word forms, making it easier to identify patterns across large text corpora.
Sentiment Analysis: Before sentiment analysis, it is used to process reviews and comments. This allows the system to analyze sentiments based on root words which improves its ability to understand positive or negative sentiments despite word variations.
Challenges in Stemming
While stemming is beneficial but also it has some challenges:

Over-Stemming: When words are reduced too aggressively, leading to the loss of meaning. For example, "arguing" becomes "argu" making it harder to understand.
Under-Stemming: Occurs when related words are not reduced to a common base form, causing inconsistencies. For example, "argument" and "arguing" might not be stemmed similarly.
Loss of Meaning: Stemming ignores context which can result in incorrect interpretations in tasks like sentiment analysis.
Choosing the Right Stemmer: Different stemmers may produce diffierent results which requires careful selection and testing for the best fit.
These challenges can be solved by fine-tuning the stemming process or using lemmatization when necessary.

Advantages of Stemming
Stemming provides various benefits which are as follows:

Text Normalization: By reducing words to their root form, it helps to normalize text which makes it easier to analyze and process.
Improved Efficiency: It reduces the dimensionality of text data which can improve the performance of machine learning algorithms.
Information Retrieval: It enhances search engine performance by ensuring that variations of the same word are treated as the same entity.
Facilitates Language Processing: It simplifies the text by reducing variations of words which makes it easier to process and analyze large text datasets.
Related Articles:
Tokenization
Removing stop words with NLTK in Python
Last Updated : 7 Oct, 2025
Natural language processing tasks often involve filtering out commonly occurring words that provide no or very little semantic value to text analysis. These words are known as stopwords include articles, prepositions and pronouns like "the", "and", "is" and "in". While they seem insignificant, proper stopword handling can dramatically impact the performance and accuracy of NLP applications.

Sample text with Stop Words	Without Stop Words
GeeksforGeeks – A Computer Science Portal for Geeks	GeeksforGeeks, Computer Science, Portal, Geeks
Can listening be exhausting?	Listening, Exhausting
I like reading, so I read	Like, Reading, read
Consider the sentence: "The quick brown fox jumps over the lazy dog"

Stopwords: "the" and "over"
Content words: "quick", "brown", "fox", "jumps", "lazy", "dog"
It becomes particularly important when dealing with large text corpora where computational efficiency matters. Processing every single word including high-frequency stopwords can consume unnecessary resources and potentially skew analysis results.

When to Remove Stopwords
The decision to remove stopwords depends heavily on the specific NLP task at hand:

Tasks that benefit from stopword removal:
Text classification and sentiment analysis
Information retrieval and search engines
Topic modelling and clustering
Keyword extraction
Tasks that require preserving stopwords:
Machine translation (maintains grammatical structure)
Text summarization (preserves sentence coherence)
Question-answering systems (syntactic relationships matter)
Grammar checking and parsing
Language modeling presents an interesting middle ground where the decision depends on the specific application requirements and available computational resources.

Categories of Stopwords
Understanding different types of stopwords helps in making informed decisions:

Standard Stopwords: Common function words like articles ("a", "the"), conjunctions ("and", "but") and prepositions ("in", "on")
Domain-Specific Stopwords: Context-dependent terms that appear frequently in specific fields like "patient" in medical texts
Contextual Stopwords: Words with extremely high frequency in particular datasets
Numerical Stopwords: Digits, punctuation marks and single characters
Implementation with NLTK
NLTK provides robust support for stopword removal across 16 different languages. The implementation involves tokenization followed by filtering:

Setup: Import NLTK modules and download required resources like stopwords and tokenizer data.
Text preprocessing: Convert the sample sentence to lowercase and tokenize it into words.
Stopword removal: Load English stopwords and filter them out from the token list.
Output: Print both the original and cleaned tokens for comparison.



import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
​
nltk.download('stopwords')
nltk.download('punkt')
​
# Sample text
text = "This is a sample sentence showing stopword removal."
​
# Get English stopwords and tokenize
stop_words = set(stopwords.words('english'))
tokens = word_tokenize(text.lower())
​
# Remove stopwords
filtered_tokens = [word for word in tokens if word not in stop_words]
​
print("Original:", tokens)
print("Filtered:", filtered_tokens)
Output:

Original: ['this', 'is', 'a', 'sample', 'sentence', 'showing', 'stopword', 'removal', '.'] 
Filtered: ['sample', 'sentence', 'showing', 'stopword', 'removal', '.']

Other Methods for Stopword Removal
Lets see various methods for stopwords removal:

1. Implementation using SpaCy
SpaCy offers a more sophisticated approach with built-in linguistic analysis:

Imports spaCy: Used for natural language processing.
Load model: Loads the English NLP model with tokenization and stopword detection.
Process text: Converts the sentence into a Doc object with linguistic features.
Remove stopwords: Filters out common words using token.is_stop.
Print output: Displays non-stopword tokens like ['researchers', 'developing', 'advanced', 'algorithms'].



import spacy
​
nlp = spacy.load("en_core_web_sm")
doc = nlp("The researchers are developing advanced algorithms.")
​
# Filter stopwords using spaCy
filtered_words = [token.text for token in doc if not token.is_stop]
print("Filtered:", filtered_words)
Output:

Filtered: ['researchers', 'developing', 'advanced', 'algorithms', '.']

2. Removing stop words with Genism
We can use Genism for stopword removal:

Import function: Brings in remove_stopwords from Gensim.
Define text: A sample sentence is used.
Apply stopword removal: Removes common words like “the,” “a”.
Print output: Shows original and filtered text.



from gensim.parsing.preprocessing import remove_stopwords
​
# Another sample text
new_text = "The majestic mountains provide a breathtaking view."
​
# Remove stopwords using Gensim
new_filtered_text = remove_stopwords(new_text)
​
print("Original Text:", new_text)
print("Text after Stopword Removal:", new_filtered_text)
Output:

Original Text: The majestic mountains provide a breathtaking view. 
Text after Stopword Removal: The majestic mountains provide breathtaking view.

3. Implementation with Scikit Learn
We can use Scikit Learn for stopword removal:

Imports necessary modules from sklearn and nltk for tokenization and stopword removal.
Defines a sample sentence
Tokenizes the sentence into individual words using NLTK's word_tokenize.
Filters out common English stopwords from the token list.
Prints both the original and stopword-removed versions of the text.



from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
​
# Another sample text
new_text = "The quick brown fox jumps over the lazy dog."
​
# Tokenize the new text using NLTK
new_words = word_tokenize(new_text)
​
# Remove stopwords using NLTK
new_filtered_words = [
    word for word in new_words if word.lower() not in stopwords.words('english')]
​
# Join the filtered words to form a clean text
new_clean_text = ' '.join(new_filtered_words)
​
print("Original Text:", new_text)
print("Text after Stopword Removal:", new_clean_text)
Output:

Original Text: The quick brown fox jumps over the lazy dog. 
Text after Stopword Removal: quick brown fox jumps lazy dog .

Among all libraries NLTK provides best performance.

Advanced Techniques and Custom Stopwords
Real-world applications often require custom stopword lists tailored to specific domains:

Imports Counter to count word frequencies.
Tokenizes all texts and flattens them into one word list.
Calculates frequency of each word.
Adds words to custom stopwords if they exceed a set frequency threshold.
Merges custom stopwords with NLTK’s default stopword list.



from collections import Counter
​
def create_custom_stopwords(texts, threshold=0.1):
    # Count word frequencies across all texts
    all_words = []
    for text in texts:
        words = word_tokenize(text.lower())
        all_words.extend(words)
    
    word_freq = Counter(all_words)
    total_words = len(all_words)
    
    # Words appearing more than threshold become stopwords
    custom_stops = {word for word, freq in word_freq.items() 
                   if freq / total_words > threshold}
    
    return custom_stops.union(set(stopwords.words('english')))
This approach identifies domain-specific high-frequency words that may not appear in standard stopword lists but function as noise in particular contexts.

Edge Cases and Limitations
Stopword removal is essential in NLP but must be handled carefully. It requires normalization (e.g., handling case and contractions) and language-specific lists for multilingual text. Removing words like "not" or certain prepositions can harm tasks such as sentiment analysis or entity recognition. Over-removal may lose valuable signals while under-removal can keep noise. Its impact varies—beneficial in classification but risky in tasks needing full semantic context.

Aspect	Details
Normalization	Handle case differences and contractions (e.g., "don't", "THE")
Language Specificity	Use stopword lists tailored to each language
Context Risk	Important words like "not" or prepositions may be needed for meaning
Signal vs. Noise	Too much removal = loss of signal or too little = extra noise
Task Sensitivity	Helps in classification but may hurt tasks needing deeper understanding
Modern deep learning approaches sometimes learn to ignore irrelevant words automatically, but traditional machine learning methods and resource-constrained applications still benefit significantly from thoughtful stopword handling.
POS(Parts-Of-Speech) Tagging in NLP
Last Updated : 17 Dec, 2025
Parts of Speech (PoS) tagging is a fundamental task in Natural Language Processing (NLP) where each word in a sentence is assigned a grammatical category such as noun, verb, adjective or adverb. This process help machines to understand the structure and meaning of sentences by identifying the roles of words and their relationships.

a_quick_brown_fox_jumps_over_a_lazy_dog.webpa_quick_brown_fox_jumps_over_a_lazy_dog.webp
It plays an important role in various NLP applications including machine translation, sentiment analysis and information retrieval, by bridging the gap between human language and machine understanding.

Key Concepts in POS Tagging
Parts of Speech: These are categories like nouns, verbs, adjectives, adverbs, etc that define the role of a word in a sentence.
Tagging: The process of assigning a specific part-of-speech label to each word in a sentence.
Corpus: A large collection of text data used to train POS taggers.
Example of POS Tagging
Consider the sentence: "The quick brown fox jumps over the lazy dog."

After performing POS Tagging, we get:

"The" is tagged as determiner (DT)
"quick" is tagged as adjective (JJ)
"brown" is tagged as adjective (JJ)
"fox" is tagged as noun (NN)
"jumps" is tagged as verb (VBZ)
"over" is tagged as preposition (IN)
"the" is tagged as determiner (DT)
"lazy" is tagged as adjective (JJ)
"dog" is tagged as noun (NN)
Each word is assigned a tag based on its role in the sentence. For example, "quick" and "brown" are adjectives that describe the noun "fox."

Working of POS Tagging
Let’s see various steps involved in POS tagging:

Tokenization: The input text is split into individual tokens (words or subwords), this step is necessary for further analysis.
Preprocessing: The text is cleaned such as converting it to lowercase and removing special characters, to improve accuracy.
Loading a Language Model: Tools like NLTK or SpaCy use pre-trained language models to understand the grammatical rules of the language, these models have been trained on large datasets.
Linguistic Analysis: The structure of the sentence is analyzed to understand the role of each word in context.
POS Tagging: Each word is assigned a part-of-speech label based on its role in the sentence and the context provided by surrounding words.
Evaluation: The results are checked for accuracy. If there are any errors or misclassifications, they are corrected.
Types of POS Tagging
There are different types and each has its strengths and use cases. Let's see few common methods:

1. Rule-Based Tagging
Rule-based POS tagging assigns POS tags based on predefined grammatical rules. These rules are crafted based on morphological features (like word endings) and syntactic context, making the approach highly interpretable and transparent.

Example:

1. Rule: Assign the POS tag "Noun" to words ending in "-tion" or "-ment".

2. Sentence: "The presentation highlighted the key achievements of the project's development."

3. Tagged Output:

"presentation" → Noun (N)
"highlighted" → Verb (V)
"development" → Noun (N)
2. Transformation-Based Tagging (TBT)
TBT refines POS tags through a series of context-based transformations. Unlike statistical taggers that rely on probabilities or rule-based taggers, it starts with initial tags and improves them iteratively by applying transformation rules.

Example:

Text: "The cat chased the mouse."
Initial Tags: "The" – DET, "cat" – NOUN, "chased" – VERB, "the" – DET, "mouse" – NOUN
Rule Applied: Change “chased” from Verb to Nounbecause it follows “the”.
Updated Tags: "chased" becomes Noun.
3. Statistical POS Tagging
It uses probabilistic models to assign grammatical categories (e.g noun, verb, adjective) to words in a text. Unlike rule-based methods which rely on handcrafted rules, it learns patterns from large annotated corpora using machine learning techniques.

These models calculate the likelihood of a tag based on a word and its context, helping to resolve ambiguities and handle complex grammar. Common models include:

Hidden Markov Models (HMMs)
Conditional Random Fields (CRFs)
Implementing POS Tagging with NLTK
Let's see step by step process how POS Tagging works with NLTK:

Step 1: Installing Required Resources
Here we import the NLTK library and download the necessary datasets using nltk.download().




import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
Step 2: Applying POS Tagging
First we store the sentence and tokenize it into words using word_tokenize(text). Then we apply POS tagging to the tokenized words using pos_tag(words). This assigns a part-of-speech to each word.




text = "NLTK is a powerful library for natural language processing."
words = word_tokenize(text)
​
pos_tags = pos_tag(words)
Step 3: Displaying Results
Now we print the original sentence and loop through the tagged words to show each word with its POS tag.




print("Original Text:")
print(text)
​
print("\nPoS Tagging Result:")
for word, pos_tag in pos_tags:
    print(f"{word}: {pos_tag}")
Output:

pos1
POS Tagging with NLTK
Implementing POS Tagging with SpaCy
Let's see step by step process how POS Tagging works with SpaCy:

Step 1: Installing and importing Required Resources
Here we install and import the SpaCy library and install the pre-trained English language model (en_core_web_sm).




!pip install spacy
!python -m spacy download en_core_web_sm
import spacy
nlp = spacy.load("en_core_web_sm")
Step 2: Defining and Processing the Text
We store the sentence in a variable and process it with nlp(text) to get linguistic annotations.




text = "SpaCy is a popular natural language processing library."
doc = nlp(text)
Step 3: Displaying POS Tagging
Print the original sentence then loop through the tokens and display each word with its POS tag.




print("Original Text: ", text)
print("PoS Tagging Result:")
for token in doc:
    print(f"{token.text}: {token.pos_}")
Output:

pos2
POS Tagging with SpaCy
Advantages of POS tagging
Text Simplification: POS tagging can break down complex sentences into simpler parts, making them easier to understand.
Improved Search: It improves information retrieval by categorizing words, making it easier to index and search text.
Named Entity Recognition (NER): It helps identify names, places and organizations by recognizing the role of words in a sentence.
Challenges of POS Tagging
Ambiguity: Words can have multiple meanings depending on the context which can make tagging difficult.
Idiomatic Expressions: Informal language and idioms may be hard to tag correctly.
Out-of-Vocabulary Words: Words that haven’t been seen before can lead to incorrect tagging.
Domain Dependence: Models may not work well outside the specific language domain they were trained on.

One-Hot Encoding in NLP
Last Updated : 7 Jan, 2026
In Natural Language Processing (NLP) textual data must be converted into numerical form so that machine learning models can process it. One-hot encoding is a simple technique used to represent words or labels as numerical vectors.

build_ideas_with_logic_and_code
One Hot Encoding in NLP
In one-hot encoding each unique word is mapped to a binary vector where only one position has the value 1 and all others are 0. The length of the vector equals the size of the vocabulary making each word uniquely identifiable.

Transforms categorical text data into numeric vectors
Each word is represented by a vector with a single 1 and remaining 0s
Easy to understand and implement
Works well for small vocabularies but becomes inefficient for large ones
How One-Hot Encoding Works
One-hot encoding converts textual data into numerical form by representing each word as a unique binary vector. The process involves the following steps:

Vocabulary Creation: First a vocabulary is created by collecting all unique words from the entire text corpus. Each word in the vocabulary is assigned a unique index.
Vector Representation: Each word is then represented as a binary vector of length equal to the vocabulary size. The index corresponding to the word is set to 1 while all other positions are set to 0 ensuring a unique representation for every word.
When to Use One-Hot Encoding
One-hot encoding is widely used in Natural Language Processing (NLP) and machine learning when categorical data needs to be converted into a numerical format for model training.

Text Classification: Used to represent words or documents numerically in tasks such as spam detection, sentiment analysis and topic classification.
Feature Engineering: Applied when categorical features must be included as input features in machine learning models.
Embedding Layers: Often used as an initial step before embedding layers in deep learning models to prepare categorical input data.
Label Encoding: Used to encode categorical target labels in classification problems so that models can process them correctly.
Step By Step Implementation
Step 1: Import Required Libraries
import numpy is used for creating vectors.
import string helps remove punctuation from text.
import matplotlib.pyplot is for visualization.

import numpy as np
import string
import matplotlib.pyplot as plt
Step 2: Define the Corpus
A corpus is a collection of sentences on which we want to perform NLP tasks.
Each sentence will later be tokenized and encoded.

corpus = [
    "The quick brown fox jumps over the lazy dog",
    "The dog chased the fox",
    "The fox is quick and smart"
]
Step 3: Preprocess Text
Convert text to lowercase to maintain consistency.
Remove punctuation to avoid treating punctuations as separate tokens.
Split the sentence into individual words.

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.split()
tokenized_corpus = [preprocess_text(sentence) for sentence in corpus]
Step 4: Build Vocabulary
A vocabulary contains all unique words across the corpus.
Sorting helps maintain a consistent order.
We also create a dictionary to map each word to a unique index.

vocabulary = sorted(set(word for sentence in tokenized_corpus for word in sentence))
word_to_index = {word: idx for idx, word in enumerate(vocabulary)}
Step 5: One-Hot Encode Sentences
For each word create a zero vector of length equal to vocabulary size.
Set the index corresponding to the word to 1.
Collect all word vectors for a sentence.

def one_hot_encode(sentence, word_to_index):
    vocab_size = len(word_to_index)
    encoded_sentence = []
    for word in sentence:
        vector = np.zeros(vocab_size, dtype=int)
        vector[word_to_index[word]] = 1
        encoded_sentence.append(vector)
    return np.array(encoded_sentence)
encoded_vectors = one_hot_encode(tokenized_corpus[0], word_to_index)
Step 6: Display Results
Print the vocabulary one-hot encoded vectors alongside their corresponding words.


print("Vocabulary:")
print(vocabulary)

print("\nOne-Hot Encoded Vectors (First Sentence):")
for word, vector in zip(tokenized_corpus[0], encoded_vectors):
    print(f"{word}: {vector}")
Output:

OHE
Output
You can download full code from here

Difference Between One Hot Encoding and Word Embeddings
Here we compare one hot encoding technique with word embedding

Parameter

One-Hot Encoding

Word Embeddings

Vector Type

Binary vector

Dense numerical vector

Vector Dimension

Equal to vocabulary size

Fixed and low

Sparsity

Highly sparse

Dense

Semantic Information

Not captured

Captured

Memory Efficiency

Low

High

Scalability

Poor for large vocabularies

Scales well

Why One-Hot Encoding is Used in NLP
One-hot encoding is used in Natural Language Processing (NLP) to convert categorical text data into numerical form enabling machine learning models to process and analyze textual information effectively.

Numerical Representation: Machine learning algorithms require numerical input and one-hot encoding converts words, tokens or part-of-speech tags into binary vectors.
Distinct Token Identification: Each word is represented uniquely ensuring no ordinal or priority relationship between tokens.
Model Compatibility: One-hot encoded vectors can be directly used as inputs to machine learning and neural network models.
Use in NLP Tasks: Commonly applied in tasks such as sentiment analysis, text classification and language modeling.
Advantages
Simple and Interpretable: Each word or category is represented using a binary vector making the encoding easy to understand and implement.
No Ordinal Bias: One-hot encoding treats all words equally and does not introduce any unintended ordering or priority among tokens.
Suitable for Categorical Data: Works well when dealing with categorical text features with a small or fixed vocabulary.
Model Compatibility: Can be directly used as input for traditional machine learning models and basic neural networks.
Foundation for NLP Pipelines: Often used as an initial text preprocessing step before applying more advanced NLP techniques.
Limitations
High Dimensionality: Large vocabularies result in very high-dimensional vectors increasing memory usage and computational cost.
Sparse Representation: Most elements in the vector are zeros leading to inefficient storage and slower model training.
No Semantic Information: Fails to capture relationships or similarities between words.
Poor Scalability: Becomes impractical for real-world NLP tasks involving millions of unique words.
Inferior to Embeddings: Modern NLP tasks prefer word embeddings which represent words as dense, low-dimensional vectors that preserve semantic meaning.

Bag of words (BoW) model in NLP
Last Updated : 22 Jan, 2026
In Natural Language Processing (NLP) text data needs to be converted into numbers so that machine learning algorithms can understand it. One common method to do this is Bag of Words (BoW) model. It turns text like sentence, paragraph or document into a collection of words and counts how often each word appears but ignoring the order of the words. It does not consider the order of the words or their grammar but focuses on counting how often each word appears in the text.

This makes it useful for tasks like text classification, sentiment analysis and clustering.

Key Components of BoW
Vocabulary: It is a list of all unique words from the entire dataset. Each word in the vocabulary corresponds to a feature in the model.
Document Representation: Each document is represented as a vector where each element shows the frequency of the words from the vocabulary in that document. The frequency of each word is used as a feature for the model.
Steps to Implement the Bag of Words (BoW) Model
Lets see how to implement the BoW model using Python. Here we will be using NLTK, Heapq, Matplotlib, Word cloud, Numpy and Seaborn libraries for this implementation.

Step 1: Preprocessing the Text
Before applying the BoW model, we need to preprocess the text. This includes:

Converting the text to lowercase
Removing non-word characters
Removing extra spaces



import nltk
import re
​
text = """Beans. I was trying to explain to somebody as we were flying in, that's corn.
         That's beans. And they were very impressed at my agricultural knowledge. 
         Please give it up for Amaury once again for that outstanding introduction. 
         I have a bunch of good friends here today, including somebody who I served with, 
         who is one of the finest senators in the country, and we're lucky to have him, 
         your Senator, Dick Durbin is here. I also noticed, by the way, 
         former Governor Edgar here, who I haven't seen in a long time, and 
         somehow he has not aged and I have. And it's great to see you, Governor. 
         I want to thank President Killeen and everybody at the U of I System for 
         making it possible for me to be here today. And I am deeply honored at the Paul 
         Douglas Award that is being given to me. He is somebody who set the path for so 
         much outstanding public service here in Illinois. Now, I want to start by 
         addressing the elephant in the room. I know people are still wondering why 
         I didn't speak at the commencement."""
​
dataset = nltk.sent_tokenize(text)
​
for i in range(len(dataset)):
    dataset[i] = dataset[i].lower()
    dataset[i] = re.sub(r'\W', ' ', dataset[i])
    dataset[i] = re.sub(r'\s+', ' ', dataset[i])
​
for i, sentence in enumerate(dataset):
    print(f"Sentence {i+1}: {sentence}")
Output:

bow11
Preprocessing the Text
Step 2: Counting Word Frequencies
In this step, we count the frequency of each word in the preprocessed text. We will store these counts in a pandas DataFrame to view them easily in a tabular format.

We initialize a dictionary to hold our word counts.
Then, we tokenize each sentence into words.
For each word, we check if it exists in our dictionary. If it does, we increment its count. If it doesn’t, we add it to the dictionary with a count of 1.



word2count = {}
​
for data in dataset:
    words = nltk.word_tokenize(data)
    for word in words:
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1
​
stop_words = set(stopwords.words('english'))
​
filtered_word2count = {word: count for word, count in word2count.items() if word not in stop_words}
​
word_freq_df = pd.DataFrame(list(filtered_word2count.items()), columns=['Word', 'Frequency'])
​
word_freq_df = word_freq_df.sort_values(by='Frequency', ascending=False)
​
print(word_freq_df)
Output:

bow2
Counting Word Frequencies
Step 3: Selecting the Most Frequent Words
Now that we have counted the word frequencies, we will select the top N most frequent words (e.g top 10) to be used in the BoW model. We can visualize these frequent words using a bar chart to understand the distribution of words in our dataset.




import heapq
import matplotlib.pyplot as plt
​
freq_words = heapq.nlargest(10, word2count, key=word2count.get)
​
print(f"Top 10 frequent words: {freq_words}")
​
top_words = sorted(word2count.items(), key=lambda x: x[1], reverse=True)[:10]
words, counts = zip(*top_words)
​
plt.figure(figsize=(10, 6))
plt.bar(words, counts, color='skyblue')
plt.xticks(rotation=45)
plt.title('Top 10 Most Frequent Words')
plt.xlabel('Words')
plt.ylabel('Frequency')
plt.show()
Output:

bow3
Selecting the Most Frequent Words
Step 4: Building the Bag of Words (BoW) Model
Now we will build the Bag of Words (BoW) model. This model is represented as a binary matrix where each row corresponds to a sentence and each column represents one of the top N frequent words. A 1 in the matrix shows that the word is present in the sentence and a 0 shows its absence.

We will use a heatmap to visualize this binary matrix where green shows the presence of a word (1) and red shows its absence (0).




import numpy as np
import seaborn as sns
​
X = []
​
for data in dataset:
    vector = []
    for word in freq_words:
        if word in nltk.word_tokenize(data):
            vector.append(1)
        else:
            vector.append(0)
    X.append(vector)
​
X = np.asarray(X)
​
plt.figure(figsize=(10, 6))
sns.heatmap(X, cmap='RdYlGn', cbar=False, annot=True, fmt="d", xticklabels=freq_words, yticklabels=[f"Sentence {i+1}" for i in range(len(dataset))])
​
plt.title('Bag of Words Matrix')
plt.xlabel('Frequent Words')
plt.ylabel('Sentences')
plt.show()
Output:

bow4
Building the Bag of Words (BoW) Model
Step 5: Visualizing Word Frequencies with a Word Cloud
Finally, we can create a Word Cloud to visually represent the word frequencies. In a word cloud, the size of each word is proportional to its frequency which makes it easy to identify the most common words at a glance.




from wordcloud import WordCloud
​
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word2count)
​
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Word Cloud of Frequent Words")
plt.show()
Output:

bow5-
Visualizing Word Frequencies with a Word Cloud
Advantages of the Bag of Words Model
Simplicity: It is easy to implement and computationally efficient.
Versatility: It can be used for various NLP tasks such as text classification, sentiment analysis and document clustering.
Interpretability: The resulting vectors are interpretable which makes it easy to understand which words are most important in a document.
Limitations of BoW
Loss of Context: It ignores word order and context which means it might miss important relationships between words.
Sparsity: When working with large datasets, most word vectors will be sparse (containing mostly zeros) which can lead to inefficiency.
Limited Semantic Understanding: The model doesn’t capture the meaning of words which can be important for some NLP tasks.

Understanding TF-IDF (Term Frequency-Inverse Document Frequency)
Last Updated : 17 Dec, 2025
TF-IDF (Term Frequency–Inverse Document Frequency) is a statistical method used in natural language processing and information retrieval to evaluate how important a word is to a document in relation to a larger collection of documents. TF-IDF combines two components:

1. Term Frequency (TF): Measures how often a word appears in a document. A higher frequency suggests greater importance. If a term appears frequently in a document, it is likely relevant to the document’s content.

The-TF-Formula
Term Frequency (TF)
2. Inverse Document Frequency (IDF): Reduces the weight of common words across multiple documents while increasing the weight of rare words. If a term appears in fewer documents, it is more likely to be meaningful and specific.

IDF-Formula
Inverse Document Frequency (IDF)
This balance allows TF-IDF to highlight terms that are both frequent within a specific document and distinctive across the text document, making it a useful tool for tasks like search ranking, text classification and keyword extraction.

Converting Text into vectors with TF-IDF
Let's take an example where we have a corpus (a collection of documents) with three documents and our goal is to calculate the TF-IDF score for specific terms in these documents.

Document 1: "The cat sat on the mat."
Document 2: "The dog played in the park."
Document 3: "Cats and dogs are great pets."
Our goal is to calculate the TF-IDF score for specific terms in these documents. Let’s focus on the word "cat" and see how TF-IDF evaluates its importance.

Step 1: Calculate Term Frequency (TF)
For Document 1:

The word "cat" appears 1 time.
The total number of terms in Document 1 is 6 ("the", "cat", "sat", "on", "the", "mat").
So, TF(cat,Document 1) = 1/6
For Document 2:

The word "cat" does not appear.
So, TF(cat,Document 2)=0.
For Document 3:

The word "cat" appears 1 time.
The total number of terms in Document 3 is 6 ("cats", "and", "dogs", "are", "great", "pets").
So TF (cat,Document 3)=1/6
In Document 1 and Document 3 the word "cat" has the same TF score. This means it appears with the same relative frequency in both documents. In Document 2 the TF score is 0 because the word "cat" does not appear.

Step 2: Calculate Inverse Document Frequency (IDF)
Total number of documents in the corpus (D): 3
Number of documents containing the term "cat": 2 (Document 1 and Document 3).
IDF(cat,D)=log \frac{3}{2}  ≈0.176

Step 3: Calculate TF-IDF
The TF-IDF score for "cat" is 0.029 in Document 1 and Document 3 and 0 in Document 2 that reflects both the frequency of the term in the document (TF) and its rarity across the corpus (IDF).

The TF-IDF score is the product of TF and IDF:

idf_formula
TF-IDF
For Document 1: TF-IDF (cat, Document 1, D)-0.167 * 0.176 - 0.029
For Document 2: TF-IDF(cat, Document 2, D)-0x 0.176-0
For Document 3: TF-IDF (cat, Document 3, D)-0.167 x 0.176 ~ 0.029
Implementing TF-IDF in Python
Step 1: Import modules
We will import scikit learn for this.


from sklearn.feature_extraction.text import TfidfVectorizer
Step 2: Collect strings from documents and create a corpus

d0 = 'Geeks for geeks'
d1 = 'Geeks'
d2 = 'r2j'
string = [d0, d1, d2]
Step 3: Get TF-IDF values
Here we are using TfidfVectorizer() from scikit learn to perform tf-idf and apply on our courpus using fit_transform.


tfidf = TfidfVectorizer()
result = tfidf.fit_transform(string)
Step 4: Display IDF values

print('\nidf values:')
for ele1, ele2 in zip(tfidf.get_feature_names_out(), tfidf.idf_):
    print(ele1, ':', ele2)
Output:



Step 5: Display TF-IDF values along with indexing

print('\nWord indexes:')
print(tfidf.vocabulary_)
print('\ntf-idf value:')
print(result)
print('\ntf-idf values in matrix form:')
print(result.toarray())
Output:

image
Output
The result variable consists of unique words as well as the tf-if values. It can be elaborated using the below image:



From the above image the below table can be generated:

Document	Word	Document Index	Word Index	tf-idf value
d0	for	0	0	0.549
d0	geeks	0	1	0.8355
d1	geeks	1	1	1.000
d2	r2j	2	2	1.000
Applications
Document Similarity and Clustering: By converting documents into numerical vectors TF-IDF enables comparison and grouping of related texts. This is valuable for clustering news articles, research papers or customer support tickets into meaningful categories.
Text Classification: It helps in identify patterns in text for spam filtering, sentiment analysis and topic classification.
Keyword Extraction: It ranks words by importance making it possible to automatically highlight key terms, generate document tags or create concise summaries.
Recommendation Systems: Through comparison of textual descriptions TF-IDF supports suggesting related articles, videos or products enhancing user engagement.

Understanding TF-IDF (Term Frequency-Inverse Document Frequency)
Last Updated : 17 Dec, 2025
TF-IDF (Term Frequency–Inverse Document Frequency) is a statistical method used in natural language processing and information retrieval to evaluate how important a word is to a document in relation to a larger collection of documents. TF-IDF combines two components:

1. Term Frequency (TF): Measures how often a word appears in a document. A higher frequency suggests greater importance. If a term appears frequently in a document, it is likely relevant to the document’s content.

The-TF-Formula
Term Frequency (TF)
2. Inverse Document Frequency (IDF): Reduces the weight of common words across multiple documents while increasing the weight of rare words. If a term appears in fewer documents, it is more likely to be meaningful and specific.

IDF-Formula
Inverse Document Frequency (IDF)
This balance allows TF-IDF to highlight terms that are both frequent within a specific document and distinctive across the text document, making it a useful tool for tasks like search ranking, text classification and keyword extraction.

Converting Text into vectors with TF-IDF
Let's take an example where we have a corpus (a collection of documents) with three documents and our goal is to calculate the TF-IDF score for specific terms in these documents.

Document 1: "The cat sat on the mat."
Document 2: "The dog played in the park."
Document 3: "Cats and dogs are great pets."
Our goal is to calculate the TF-IDF score for specific terms in these documents. Let’s focus on the word "cat" and see how TF-IDF evaluates its importance.

Step 1: Calculate Term Frequency (TF)
For Document 1:

The word "cat" appears 1 time.
The total number of terms in Document 1 is 6 ("the", "cat", "sat", "on", "the", "mat").
So, TF(cat,Document 1) = 1/6
For Document 2:

The word "cat" does not appear.
So, TF(cat,Document 2)=0.
For Document 3:

The word "cat" appears 1 time.
The total number of terms in Document 3 is 6 ("cats", "and", "dogs", "are", "great", "pets").
So TF (cat,Document 3)=1/6
In Document 1 and Document 3 the word "cat" has the same TF score. This means it appears with the same relative frequency in both documents. In Document 2 the TF score is 0 because the word "cat" does not appear.

Step 2: Calculate Inverse Document Frequency (IDF)
Total number of documents in the corpus (D): 3
Number of documents containing the term "cat": 2 (Document 1 and Document 3).
IDF(cat,D)=log \frac{3}{2}  ≈0.176

Step 3: Calculate TF-IDF
The TF-IDF score for "cat" is 0.029 in Document 1 and Document 3 and 0 in Document 2 that reflects both the frequency of the term in the document (TF) and its rarity across the corpus (IDF).

The TF-IDF score is the product of TF and IDF:

idf_formula
TF-IDF
For Document 1: TF-IDF (cat, Document 1, D)-0.167 * 0.176 - 0.029
For Document 2: TF-IDF(cat, Document 2, D)-0x 0.176-0
For Document 3: TF-IDF (cat, Document 3, D)-0.167 x 0.176 ~ 0.029
Implementing TF-IDF in Python
Step 1: Import modules
We will import scikit learn for this.


from sklearn.feature_extraction.text import TfidfVectorizer
Step 2: Collect strings from documents and create a corpus

d0 = 'Geeks for geeks'
d1 = 'Geeks'
d2 = 'r2j'
string = [d0, d1, d2]
Step 3: Get TF-IDF values
Here we are using TfidfVectorizer() from scikit learn to perform tf-idf and apply on our courpus using fit_transform.


tfidf = TfidfVectorizer()
result = tfidf.fit_transform(string)
Step 4: Display IDF values

print('\nidf values:')
for ele1, ele2 in zip(tfidf.get_feature_names_out(), tfidf.idf_):
    print(ele1, ':', ele2)
Output:



Step 5: Display TF-IDF values along with indexing

print('\nWord indexes:')
print(tfidf.vocabulary_)
print('\ntf-idf value:')
print(result)
print('\ntf-idf values in matrix form:')
print(result.toarray())
Output:

image
Output
The result variable consists of unique words as well as the tf-if values. It can be elaborated using the below image:



From the above image the below table can be generated:

Document	Word	Document Index	Word Index	tf-idf value
d0	for	0	0	0.549
d0	geeks	0	1	0.8355
d1	geeks	1	1	1.000
d2	r2j	2	2	1.000
Applications
Document Similarity and Clustering: By converting documents into numerical vectors TF-IDF enables comparison and grouping of related texts. This is valuable for clustering news articles, research papers or customer support tickets into meaningful categories.
Text Classification: It helps in identify patterns in text for spam filtering, sentiment analysis and topic classification.
Keyword Extraction: It ranks words by importance making it possible to automatically highlight key terms, generate document tags or create concise summaries.
Recommendation Systems: Through comparison of textual descriptions TF-IDF supports suggesting related articles, videos or products enhancing user engagement.
Understanding TF-IDF (Term Frequency-Inverse Document Frequency)
Last Updated : 17 Dec, 2025
TF-IDF (Term Frequency–Inverse Document Frequency) is a statistical method used in natural language processing and information retrieval to evaluate how important a word is to a document in relation to a larger collection of documents. TF-IDF combines two components:

1. Term Frequency (TF): Measures how often a word appears in a document. A higher frequency suggests greater importance. If a term appears frequently in a document, it is likely relevant to the document’s content.

The-TF-Formula
Term Frequency (TF)
2. Inverse Document Frequency (IDF): Reduces the weight of common words across multiple documents while increasing the weight of rare words. If a term appears in fewer documents, it is more likely to be meaningful and specific.

IDF-Formula
Inverse Document Frequency (IDF)
This balance allows TF-IDF to highlight terms that are both frequent within a specific document and distinctive across the text document, making it a useful tool for tasks like search ranking, text classification and keyword extraction.

Converting Text into vectors with TF-IDF
Let's take an example where we have a corpus (a collection of documents) with three documents and our goal is to calculate the TF-IDF score for specific terms in these documents.

Document 1: "The cat sat on the mat."
Document 2: "The dog played in the park."
Document 3: "Cats and dogs are great pets."
Our goal is to calculate the TF-IDF score for specific terms in these documents. Let’s focus on the word "cat" and see how TF-IDF evaluates its importance.

Step 1: Calculate Term Frequency (TF)
For Document 1:

The word "cat" appears 1 time.
The total number of terms in Document 1 is 6 ("the", "cat", "sat", "on", "the", "mat").
So, TF(cat,Document 1) = 1/6
For Document 2:

The word "cat" does not appear.
So, TF(cat,Document 2)=0.
For Document 3:

The word "cat" appears 1 time.
The total number of terms in Document 3 is 6 ("cats", "and", "dogs", "are", "great", "pets").
So TF (cat,Document 3)=1/6
In Document 1 and Document 3 the word "cat" has the same TF score. This means it appears with the same relative frequency in both documents. In Document 2 the TF score is 0 because the word "cat" does not appear.

Step 2: Calculate Inverse Document Frequency (IDF)
Total number of documents in the corpus (D): 3
Number of documents containing the term "cat": 2 (Document 1 and Document 3).
IDF(cat,D)=log \frac{3}{2}  ≈0.176

Step 3: Calculate TF-IDF
The TF-IDF score for "cat" is 0.029 in Document 1 and Document 3 and 0 in Document 2 that reflects both the frequency of the term in the document (TF) and its rarity across the corpus (IDF).

The TF-IDF score is the product of TF and IDF:

idf_formula
TF-IDF
For Document 1: TF-IDF (cat, Document 1, D)-0.167 * 0.176 - 0.029
For Document 2: TF-IDF(cat, Document 2, D)-0x 0.176-0
For Document 3: TF-IDF (cat, Document 3, D)-0.167 x 0.176 ~ 0.029
Implementing TF-IDF in Python
Step 1: Import modules
We will import scikit learn for this.


from sklearn.feature_extraction.text import TfidfVectorizer
Step 2: Collect strings from documents and create a corpus

d0 = 'Geeks for geeks'
d1 = 'Geeks'
d2 = 'r2j'
string = [d0, d1, d2]
Step 3: Get TF-IDF values
Here we are using TfidfVectorizer() from scikit learn to perform tf-idf and apply on our courpus using fit_transform.


tfidf = TfidfVectorizer()
result = tfidf.fit_transform(string)
Step 4: Display IDF values

print('\nidf values:')
for ele1, ele2 in zip(tfidf.get_feature_names_out(), tfidf.idf_):
    print(ele1, ':', ele2)
Output:



Step 5: Display TF-IDF values along with indexing

print('\nWord indexes:')
print(tfidf.vocabulary_)
print('\ntf-idf value:')
print(result)
print('\ntf-idf values in matrix form:')
print(result.toarray())
Output:

image
Output
The result variable consists of unique words as well as the tf-if values. It can be elaborated using the below image:



From the above image the below table can be generated:

Document	Word	Document Index	Word Index	tf-idf value
d0	for	0	0	0.549
d0	geeks	0	1	0.8355
d1	geeks	1	1	1.000
d2	r2j	2	2	1.000
Applications
Document Similarity and Clustering: By converting documents into numerical vectors TF-IDF enables comparison and grouping of related texts. This is valuable for clustering news articles, research papers or customer support tickets into meaningful categories.
Text Classification: It helps in identify patterns in text for spam filtering, sentiment analysis and topic classification.
Keyword Extraction: It ranks words by importance making it possible to automatically highlight key terms, generate document tags or create concise summaries.
Recommendation Systems: Through comparison of textual descriptions TF-IDF supports suggesting related articles, videos or products enhancing user engagement.
N-Gram Language Modelling with NLTK
Last Updated : 1 Aug, 2025
Language modeling involves determining the probability of a sequence of words. It is fundamental to many Natural Language Processing (NLP) applications such as speech recognition, machine translation and spam filtering where predicting or ranking the likelihood of phrases and sentences is crucial.

N-gram
N-gram is a language modelling technique that is defined as the contiguous sequence of n items from a given sample of text or speech. The N-grams are collected from a text or speech corpus. Items can be:

Words like “This”, “article”, “is”, “on”, “NLP” → unigrams
Word pairs likw “This article”, “article is”, “is on”, “on NLP” → bigrams
Triplets (trigrams) or larger combinations
N-gram Language Model
N-gram models predict the probability of a word given the previous n−1 words. For example, a trigram model uses the preceding two words to predict the next word:

Goal: Calculate p ( w | h ), the probability that the next word is w, given context/history h.

Example: For the phrase: “This article is on…”, if we want to predict the likelihood of “NLP” as the next word:

p(\text"NLP"|"This","article","is","on") 

Chain Rule of Probability
The probability of a sequence of words is computed as:

P(w_1, w_2, \ldots, w_n) = \prod_{i=1}^{n} P(w_i \mid w_1, w_2, \ldots, w_{i-1}) 

Markov Assumption
To reduce complexity, N-gram models assume the probability of a word depends only on the previous n−1 words.

P(w_i \mid w_1, \ldots, w_{i-1}) \approx P(w_i \mid w_{i-(n-1)}, \ldots, w_{i-1}) 

Evaluating Language Models
1. Entropy: Measures the uncertainty or information content in a distribution.

H(p) = \sum_x p(x) \cdot \left(-\log(p(x))\right) 

It always give non negative.

2. Cross-Entropy: Measures how well a probability distribution predicts a sample from test data.

H(p, q) = -\sum_x p(x) \log(q(x)) 

Usually ≥ entropy; reflects model “surprise” at the test data.

3. Perplexity: Exponential of cross-entropy; lower values indicate a better model.

\text{Perplexity}(W) = \sqrt[N]{\prod_{i=1}^{N} \frac{1}{P(w_i \mid w_{i-1})}} 

Implementing N-Gram Language Modelling in NLTK
words = nltk.word_tokenize(' '.join(reuters.words())): tokenizes the entire Reuters corpus into words
tri_grams = list(trigrams(words)): creates 3-word sequences from the tokenized words
model = defaultdict(lambda: defaultdict(lambda: 0)): initializes nested dictionary for trigram counts
model[(w1, w2)][w3] += 1: counts occurrences of third word w3 after (w1, w2)
model[w1_w2][w3] /= total_count: converts counts to probabilities
return max(next_word_probs, key=next_word_probs.get): returns the most likely next word based on highest probability

import nltk
from nltk import trigrams
from nltk.corpus import reuters
from collections import defaultdict

nltk.download('reuters')
nltk.download('punkt')

words = nltk.word_tokenize(' '.join(reuters.words()))
tri_grams = list(trigrams(words))

model = defaultdict(lambda: defaultdict(lambda: 0))
for w1, w2, w3 in tri_grams:
    model[(w1, w2)][w3] += 1

for w1_w2 in model:
    total_count = float(sum(model[w1_w2].values()))
    for w3 in model[w1_w2]:
        model[w1_w2][w3] /= total_count


def predict_next_word(w1, w2):
    next_word_probs = model[w1, w2]
    if next_word_probs:
        return max(next_word_probs, key=next_word_probs.get)
    else:
        return "No prediction available"


print("Next Word:", predict_next_word('the', 'stock'))
Output:

Next Word: of

Advantages
Simple and Fast: Easy to build and fast to run for small n.
Interpretable: Easy to understand and debug.
Good Baseline: Useful as a starting point for many NLP tasks.
Limitations
Limited Context: Only considers a few previous words, missing long-range dependencies.
Data Sparsity: Needs lots of data; rare n-grams are common as n increases.
High Memory: Bigger n-gram models require lots of storage.
Poor with Unseen Words: Struggles with new or rare words unless smoothing is applied.
Word Embedding using Word2Vec
Last Updated : 4 Oct, 2025
Word2Vec is a word embedding technique in natural language processing (NLP) that allows words to be represented as vectors in a continuous vector space. Researchers at Google developed word2Vec that maps words to high-dimensional vectors to capture the semantic relationships between words. It works on the principle that words with similar meanings should have similar vector representations. Word2Vec utilizes two architectures:

1. CBOW (Continuous Bag of Words)
The CBOW model predicts the current word given context words within a specific window. The input layer contains the context words and the output layer contains the current word. The hidden layer contains the dimensions we want to represent the current word present at the output layer. 

CBOW
CBOW (Continuous Bag of Words)
2. Skip Gram
The Skip gram predicts the surrounding context words within specific window given current word. The input layer contains the current word and the output layer contains the context words. The hidden layer contains the number of dimensions in which we want to represent current word present at the input layer.

output
Skip Gram
Implementation of Word2Vec
We will implement word2vec using Python programming language.

You can download the text file used for generating word vectors from here. 

1. Importing Required Libraries
We will import necessary NLTK and Gensim for building the Word2Vec model and processing text:

Word2Vec from gensim to build the word vector model.
nltk.tokenize helps in splitting text into sentences and words.
warnings is used to suppress irrelevant warnings during execution.



from gensim.models import Word2Vec
import gensim
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt_tab')
import warnings
​
warnings.filterwarnings(action='ignore')
2. Loading and Cleaning the Dataset
We will load the text data from a zip file, clean it by removing newline characters and prepare it for tokenization. We will replace newline characters (\n) with spaces to ensure the sentences are properly formatted.

zipfile.ZipFile: reads the zip file.
open(file_name): extract the content of the first file inside the zip and decode it.



import zipfile
​
with zipfile.ZipFile("/content/Gutenburg.zip", 'r') as zip_ref:
    file_name = zip_ref.namelist()[0]
    with zip_ref.open(file_name) as file:
        content = file.read().decode('utf-8', errors='ignore')
        cleaned_text = content.replace("\n", " ")
        print("File loaded")
Output:

File loaded

3. Text Tokenization
We will tokenize the cleaned text into sentences and words. We will append these tokenized words into a list, where each sentence is a sublist.

sent_tokenize(): Splits the text into sentences.
word_tokenize(): Tokenizes each sentence into words.
.lower(): Converts each word into lowercase to ensure uniformity.



data = []
​
for i in sent_tokenize(cleaned_text):
    temp = []
​
    # tokenize the sentence into words
    for j in word_tokenize(i):
        temp.append(j.lower())
​
    data.append(temp)
4. Building Word2Vec Models
We will build a Word2Vec model using both CBOW and Skip-Gram architecture one by one.

4.1. Using CBOW Model

We will be using the CBOW architecture:

min_count=1: Includes words that appear at least once.
vector_size=100: Generates word vectors of 100 dimensions.
window=5: Considers a context window of 5 words before and after the target word.
sg=0: Uses CBOW model (default setting).



model1 = gensim.models.Word2Vec(data, min_count=1,
                                vector_size=100, window=5)

4.2. Using Skip-Gram Model

We will be using the Skip-Gram architecture for this model.

min_count=1: Includes words that appear at least once.
vector_size=100: Generates word vectors of 100 dimensions.
window=5: Considers a context window of 5 words.
sg=1: Enables the Skip-Gram model (predicts context words given a target word).



model2 = gensim.models.Word2Vec(data, min_count=1, vector_size=100,
                                window=5, sg=1)
6. Evaluating Word Similarities
We will compute the cosine similarity between word vectors to assess semantic similarity. Cosine similarity values range from -1 (opposite) to 1 (very similar), showing how closely related two words are in terms of meaning.

model.wv.similarity(word1, word2): Computes the cosine similarity between word1 and word2 based on the trained model.



print("Cosine similarity between 'alice' " +
      "and 'wonderland' - CBOW : ",
      model1.wv.similarity('alice', 'wonderland'))
​
print("Cosine similarity between 'alice' " +
      "and 'machines' - CBOW : ",
      model1.wv.similarity('alice', 'machines'))
Output :

wordembedding1
Cosine similarity between words
Output indicates the cosine similarities between word vectors ‘alice’, ‘wonderland’ and ‘machines' for different models. One interesting task might be to change the parameter values of ‘size’ and ‘window’ to observe the variations in the cosine similarities.  

Applications of Word Embedding:
Text classification: Using word embeddings to increase the precision of tasks such as topic categorization and sentiment analysis.
Named Entity Recognition (NER): Using word embeddings semantic context to improve the identification of entities such as names and locations.
Information Retrieval: To provide more precise search results, embeddings are used to index and retrieve documents based on semantic similarity.
Machine Translation: The process of comprehending and translating the semantic relationships between words in various languages by using word embeddings.
Question Answering: Increasing response accuracy and understanding of semantic context in Q&A systems.
Word Embedding using Word2Vec
Last Updated : 4 Oct, 2025
Word2Vec is a word embedding technique in natural language processing (NLP) that allows words to be represented as vectors in a continuous vector space. Researchers at Google developed word2Vec that maps words to high-dimensional vectors to capture the semantic relationships between words. It works on the principle that words with similar meanings should have similar vector representations. Word2Vec utilizes two architectures:

1. CBOW (Continuous Bag of Words)
The CBOW model predicts the current word given context words within a specific window. The input layer contains the context words and the output layer contains the current word. The hidden layer contains the dimensions we want to represent the current word present at the output layer. 

CBOW
CBOW (Continuous Bag of Words)
2. Skip Gram
The Skip gram predicts the surrounding context words within specific window given current word. The input layer contains the current word and the output layer contains the context words. The hidden layer contains the number of dimensions in which we want to represent current word present at the input layer.

output
Skip Gram
Implementation of Word2Vec
We will implement word2vec using Python programming language.

You can download the text file used for generating word vectors from here. 

1. Importing Required Libraries
We will import necessary NLTK and Gensim for building the Word2Vec model and processing text:

Word2Vec from gensim to build the word vector model.
nltk.tokenize helps in splitting text into sentences and words.
warnings is used to suppress irrelevant warnings during execution.



from gensim.models import Word2Vec
import gensim
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt_tab')
import warnings
​
warnings.filterwarnings(action='ignore')
2. Loading and Cleaning the Dataset
We will load the text data from a zip file, clean it by removing newline characters and prepare it for tokenization. We will replace newline characters (\n) with spaces to ensure the sentences are properly formatted.

zipfile.ZipFile: reads the zip file.
open(file_name): extract the content of the first file inside the zip and decode it.



import zipfile
​
with zipfile.ZipFile("/content/Gutenburg.zip", 'r') as zip_ref:
    file_name = zip_ref.namelist()[0]
    with zip_ref.open(file_name) as file:
        content = file.read().decode('utf-8', errors='ignore')
        cleaned_text = content.replace("\n", " ")
        print("File loaded")
Output:

File loaded

3. Text Tokenization
We will tokenize the cleaned text into sentences and words. We will append these tokenized words into a list, where each sentence is a sublist.

sent_tokenize(): Splits the text into sentences.
word_tokenize(): Tokenizes each sentence into words.
.lower(): Converts each word into lowercase to ensure uniformity.



data = []
​
for i in sent_tokenize(cleaned_text):
    temp = []
​
    # tokenize the sentence into words
    for j in word_tokenize(i):
        temp.append(j.lower())
​
    data.append(temp)
4. Building Word2Vec Models
We will build a Word2Vec model using both CBOW and Skip-Gram architecture one by one.

4.1. Using CBOW Model

We will be using the CBOW architecture:

min_count=1: Includes words that appear at least once.
vector_size=100: Generates word vectors of 100 dimensions.
window=5: Considers a context window of 5 words before and after the target word.
sg=0: Uses CBOW model (default setting).



model1 = gensim.models.Word2Vec(data, min_count=1,
                                vector_size=100, window=5)

4.2. Using Skip-Gram Model

We will be using the Skip-Gram architecture for this model.

min_count=1: Includes words that appear at least once.
vector_size=100: Generates word vectors of 100 dimensions.
window=5: Considers a context window of 5 words.
sg=1: Enables the Skip-Gram model (predicts context words given a target word).



model2 = gensim.models.Word2Vec(data, min_count=1, vector_size=100,
                                window=5, sg=1)
6. Evaluating Word Similarities
We will compute the cosine similarity between word vectors to assess semantic similarity. Cosine similarity values range from -1 (opposite) to 1 (very similar), showing how closely related two words are in terms of meaning.

model.wv.similarity(word1, word2): Computes the cosine similarity between word1 and word2 based on the trained model.



print("Cosine similarity between 'alice' " +
      "and 'wonderland' - CBOW : ",
      model1.wv.similarity('alice', 'wonderland'))
​
print("Cosine similarity between 'alice' " +
      "and 'machines' - CBOW : ",
      model1.wv.similarity('alice', 'machines'))
Output :

wordembedding1
Cosine similarity between words
Output indicates the cosine similarities between word vectors ‘alice’, ‘wonderland’ and ‘machines' for different models. One interesting task might be to change the parameter values of ‘size’ and ‘window’ to observe the variations in the cosine similarities.  

Applications of Word Embedding:
Text classification: Using word embeddings to increase the precision of tasks such as topic categorization and sentiment analysis.
Named Entity Recognition (NER): Using word embeddings semantic context to improve the identification of entities such as names and locations.
Information Retrieval: To provide more precise search results, embeddings are used to index and retrieve documents based on semantic similarity.
Machine Translation: The process of comprehending and translating the semantic relationships between words in various languages by using word embeddings.
Question Answering: Increasing response accuracy and understanding of semantic context in Q&A systems.
Glove Word Embedding in NLP
Last Updated : 12 Aug, 2025
GloVe (Global Vectors for Word Representation) is an unsupervised learning algorithm designed to generate dense vector representations also known as embeddings. Its primary objective is to capture semantic relationships between words by analyzing their co-occurrence patterns in a large text corpus.

GloVe approach is unique as it effectively combines the strengths of two major approaches:

Latent Semantic Analysis (LSA) which uses global statistical information.
Context-based models like Word2Vec which focuses on local word context.
For instance, the relationship captured in a vector equation can be like: king - man + woman = queen.

It constructs a word co-occurrence matrix where each element reflects how often a pair of words appears together within a given context window. It then optimizes the word vectors such that the dot product between any two word vectors approximates the pointwise mutual information (PMI) of the corresponding word pair. This optimization allows GloVe to produce embeddings that effectively encode both syntactic and semantic relationships across the vocabulary.

Understanding Glove Data
Glove has pre-defined dense vectors for around every 6 billion words of English literature along with many other characters like commas, braces and semicolons. It can be downloaded and used immediately in many natural language processing (NLP) applications. Users can select a pre-trained GloVe embedding in a dimension like 50d, 100d, 200d or 300d vectors that best fits their needs in terms of computational resources and task specificity.

Here "d " stands for dimension. 100d means in this file each word has an equivalent vector of size 100.

How GloVe works ?
The GloVe algorithm works using the following process:

1. Preprocess the Text
First, we split the text into individual words (tokenization) so that we can work with them.

Example:

Input text: "The peon is ringing the bell"
Tokenized words: ['The', 'peon', 'is', 'ringing', 'the', 'bell']

2. Creating the Vocabulary
After tokenization, we create a list of all unique words in the text and then count how often each word appears.

Example:

Vocabulary with word frequencies:
{'The': 2, 'peon': 1, 'is': 1, 'ringing': 1, 'the': 1, 'bell': 1}

After this, the words are typically sorted by frequency.

3. Building a Co-occurrence Matrix:
Now, we build a co-occurrence matrix where we count how often each word appears near other words in a given context (usually within a window of fixed size around the word).

Example: Let's say we choose a window size of 2 (2 words before and after each word). The co-occurrence matrix might look something like this:

The	peon	is	ringing	the	bell
The	0	1	1	1	1	0
peon	1	0	1	1	0	0
is	1	1	0	1	1	0
ringing	1	1	1	0	1	1
the	1	0	1	1	0	1
bell	0	0	0	1	1	0
In this matrix, the value at (i, j) represents how often word i and word j appear together in the context window.

4. Performing Dot Product
The aim is to learn word vectors such that the dot product of two word vectors reflects how often the words co-occur in the context. This ensures that words that appear in similar contexts will have similar vector representations.

Example:

"The" and "is" are frequently seen together, so their vectors will be close in the embedding space.

"peon" and "bell" don't co-occur much, so their vectors will be far apart.

5. Training the Word Vectors
Now, the model optimizes the word vectors by minimizing the difference between the dot product of word vectors and the expected co-occurrence probabilities (calculated as Pointwise Mutual Information, PMI). The goal is to adjust the vectors so that they correctly reflect the relationship between words based on the co-occurrence matrix.

Example:

"The" and "is" will have vector adjustments that make their dot product similar to their co-occurrence probability, ensuring their vectors are close to each other.

"peon" and "bell" will be adjusted to have distant vectors since their co-occurrence is low.

6. Embedding Matrix
After training, the model outputs an embedding matrix where each word is represented by a dense vector. These vectors are able to capture the semantic and syntactic relationships between words.

Example: The resulting word vectors in the embedding matrix might look like this:

Word	Vector
The	[0.3, 0.1, 0.5]
peon	[0.2, 0.4, 0.3]
is	[0.6, 0.3, 0.4]
ringing	[0.1, 0.8, 0.7]
the	[0.3, 0.1, 0.5]
bell	[0.2, 0.3, 0.1]
Code Implementation
Here we will see step by step implementation

1. Importing Libraries
We will be importing necessary libraries to handle text processing and numerical operations.

Tokenizer and pad_sequences from tensorflow.keras.preprocessing.text help us tokenize the text and manage sequences of tokens, respectively.
numpy is used for handling numerical operations, especially creating and manipulating arrays like the embedding matrix.



from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
2. Creating Vocabulary
We will be defining a list of words (texts) that we want to use for building a vocabulary. These words represent our small sample text corpus that the tokenizer will later process.




texts = ['text', 'the', 'leader', 'prime', 'natural', 'language']
3. Initializing and Fitting the Tokenizer
We will be initializing the Tokenizer object and fitting it on the texts corpus to create a dictionary of words and their corresponding integer indices. The tokenizer will break the words into unique tokens and assign each token an integer ID.

The fit_on_texts function processes the provided corpus and generates the word-to-index mapping.
tokenizer.word_index gives the dictionary that maps each word to its corresponding index.



tokenizer = Tokenizer()
tokenizer.fit_on_texts(texts)
​
print("Number of unique words in dictionary =", len(tokenizer.word_index))
print("Dictionary is =", tokenizer.word_index)
Output:

Number of unique words in dictionary = 6
Dictionary is = {'text': 1, 'the': 2, 'leader': 3, 'prime': 4, 'natural': 5, 'language': 6}

4. Defining a Function to Create Embedding Matrix
We will be defining the function embedding_for_vocab that loads pre-trained GloVe word vectors and creates an embedding matrix for the vocabulary.

filepath: Path to the GloVe file.
word_index: The dictionary created by the tokenizer, mapping words to indices.
embedding_dim: The dimensionality of the word vectors (e.g., 50-dimensional vectors).
Inside the function:

We initialize a matrix of zeros with shape (vocab_size, embedding_dim) where vocab_size is the number of words plus one (to account for the padding token).
We read the GloVe file line by line and match the word to the tokenizer's word index, copying the corresponding word vector to the embedding matrix.



def embedding_for_vocab(filepath, word_index, embedding_dim):
    vocab_size = len(word_index) + 1  # +1 for padding token (index 0)
    embedding_matrix_vocab = np.zeros((vocab_size, embedding_dim))
​
    with open(filepath, encoding="utf8") as f:
        for line in f:
            word, *vector = line.split()
            if word in word_index:
                idx = word_index[word]
                embedding_matrix_vocab[idx] = np.array(vector, dtype=np.float32)[:embedding_dim]
​
    return embedding_matrix_vocab
5. Downloading GloVe File
We will be downloading the GloVe dataset from Stanford's NLP repository. This dataset contains pre-trained word embeddings, and we will be specifically using the 50-dimensional embeddings (glove.6B.50d.txt).

!wget is used to download the file.
!unzip is used to extract the zipped GloVe file.



!wget https://downloads.cs.stanford.edu/nlp/data/glove.6B.zip
!unzip -q glove.6B.zip
Output:

Screenshot-2025-07-02-131528
GloVe File
6. Loading GloVe Embeddings and Creating a Matrix
We will be specifying the embedding dimension (50 in this case, matching the GloVe file) and providing the path to the GloVe file. We then call the previously defined function embedding_for_vocab to load the GloVe embeddings and generate the embedding matrix for our vocabulary.




embedding_dim = 50 # match this with glove file
glove_path = './glove.6B.50d.txt'
​
embedding_matrix_vocab = embedding_for_vocab(glove_path, tokenizer.word_index, embedding_dim)
7. Accessing Embedding Vector for a Word
We will be accessing the embedding vector for a specific word in the tokenizer’s index. In this case, we're accessing the vector for the word with index 1, which corresponds to the word "text" in the vocabulary.




first_word_index = 1  # Tokenizer indexes start from 1
print("Dense vector for word with index 1 =>", embedding_matrix_vocab[first_word_index])
GloVe-output2
Dense embeddings of word at index - 1
Applications of GloVe Embeddings
GloVe embeddings are widely used in various NLP tasks due to their ability to capture word semantics. Key applications include:

Text Classification: Used for tasks like sentiment analysis, topic classification and spam detection.
Named Entity Recognition (NER): Enhances entity identification by capturing word relationships.
Machine Translation: Improves translation quality by representing words in source and target languages.
Question Answering: Helps models understand word context for more accurate answers.
Document Similarity and Clustering: Measures semantic similarity for document retrieval and organization.
Word Analogy: Helps solve tasks like "king - man + woman = queen" by recognizing word relationships.
Semantic Search: Improves search by retrieving content based on semantic relevance to a query.

Overview of Word Embedding using Embeddings from Language Models (ELMo)
Last Updated : 21 Jul, 2025
Word embeddings enable models to interpret text by converting words into numerical vectors. Traditional methods like Word2Vec and GloVe generate fixed embeddings, assigning the same vector to a word regardless of its context.

ELMo (Embeddings from Language Models) addresses this limitation by producing contextualized embeddings that vary based on surrounding words. This approach allows models to better capture the meaning of words in different contexts, improving performance in tasks like sentiment analysis, named entity recognition and question answering.

ELMo
ELMo (Embeddings from Language Models) generates word vectors by considering the entire sentence. Unlike traditional methods, ELMo derives word meanings from the internal states of a deep bi-directional LSTM network trained as a language model. Its Key characteristics are:

Context-aware: Word meaning changes with context.
Deep Representations: Uses multiple layers from the language model.
Pre-trained + Task-specific: ELMo embeddings are integrated into downstream models and fine-tuned accordingly.
Working of ELMo
1. Pre-training Phase
A bidirectional language model (biLM) is trained on a large text corpus. The model uses two separate LSTMs:

The forward LSTM reads the sentence from left to right and predicts the next word.
The backward LSTM reads from right to left and predicts the previous word.
Bidirectional-Recurrent-Neural-Network-2
biLM architecture
For each word, the model captures contextual information from both directions. The hidden states from the forward and backward LSTMs are summed up to form a contextualized embedding. These embeddings vary depending on the word’s role in the sentence. ELMo also combines outputs from multiple LSTM layers, capturing both syntactic and semantic patterns.

2. Task-specific Integration
Once trained, the biLM is used to generate embeddings for specific NLP tasks.

ELMo embeddings are added to the input of a downstream model, such as a classifier.
biLM can be either frozen to preserve general knowledge or fine-tuned on the specific task to improve performance.
The downstream model learns to use these embeddings for improved predictions.
This phase allows ELMo to be applied to tasks like named entity recognition, sentiment analysis and text classification where understanding context is crucial.

Real-World Examples
Consider the word "bank" in two different contexts:

"She deposited money in the bank." \rightarrow financial institution
"He sat by the bank of the river." \rightarrow river edge
Static embeddings would assign the same vector to both, failing to capture the difference. ELMo generates context-dependent vectors which correctly differentiates between these meanings. It adapts based on sentence-level context, providing more accurate representations.

Implementation of ELMo Embeddings
We can implement ELMo embeddings using TensorFlow and TensorFlow Hub. Here is a step-by-step guide with explanations at each stage.

Step 1: Install Required Libraries
Tensorflow is used for building and running deep learning models and tensorflow_hub allows us to load pretrained models such as ELMo. You can install it using:

pip install tensorflow tensorflow_hub

Step 2: Import Libraries and Load ELMo
We import TensorFlow and TensorFlow Hub to access the model.
We then load the ELMo model from TensorFlow Hub using its URL.
The model outputs 1024-dimensional embeddings for each token.



import tensorflow as tf
import tensorflow_hub as hub
​
elmo = hub.load("https://tfhub.dev/google/elmo/3")
Step 3: Define an Embedding Function
We define a function that:

Takes a list of input sentences.
Passes them to the ELMo model.
Returns a tensor of contextualized word embeddings.



def get_elmo_embedding(sentences):
    embeddings = elmo.signatures["default"](tf.constant(sentences))["elmo"]
    return embeddings
Step 4: Generate Embeddings from Sample Sentences
We create a list of sample sentences that include ambiguous words like "bank".
We call the get_elmo_embedding() function to generate the embeddings.
The result is a 3D tensor with shape (batch_size, max_seq_length, 1024).



sentences = [
    "The bank will approve your loan.",
    "He sat by the bank of the river."
]
​
embeddings = get_elmo_embedding(sentences)
print(embeddings)
Output:

ELMo-O1
Embeddings matrix
We can see that our model is working fine.

Limitations
Ambiguous Contexts: Some sentences may not provide enough information for accurate disambiguation. For example, "The bank was full of fish." could still confuse the model.
Computational Overhead: ELMo requires more memory and processing due to biLSTM layers, which can be a constraint in real-time applications.
Pretraining Dependency: Performance heavily depends on the quality and size of the pretraining corpus.
Applications of ELMo Embeddings
ELMo significantly improves performance across a variety of NLP tasks:

Sentiment Analysis: Detects emotions in text with context-aware understanding.
Named Entity Recognition (NER): Identifies names of people, places and organizations more accurately.
Question Answering: Helps locate contextually relevant answers in large documents.
Text Classification: Enhances accuracy in spam detection, topic classification and intent analysis.
Semantic Similarity: Measures context-specific similarity between phrases or documents.
Comparison with Other Models
Feature	Word2Vec / GloVe	ELMo	BERT / RoBERTa
Contextual	Static word representation	Contextualized based on sentence context	Contextualized based on full input
Architecture	Shallow neural networks	Bidirectional LSTM language model	Transformer-based
Training Objective	Word co-occurrence prediction	Forward and backward language modeling	Masked language modeling
Model Complexity	Low	Moderate	High
Fine-tuning	Not designed for fine-tuning	Supports task-specific fine-tuning	Designed for fine-tuning
ELMo introduced the idea of context in word meanings and still influences modern NLP although it has been surpassed by transformer-based models like BERT and RoBERTa in recent years.

