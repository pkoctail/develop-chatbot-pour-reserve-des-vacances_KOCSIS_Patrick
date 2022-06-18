L'objectif de ce projet est de construire un chatbot MVP qui aidera les gens à réserver facilement un billet d'avion pour leurs vacances.

La première version sera capable d'identifier les cinq éléments suivants dans la requête de l'utilisateur :
1) Ville de départ
2) Ville de destination
3) Date du vol aller
4) Date de retour du vol
5) Budget maximum
 
Le service cognitif LUIS sera utilisé pour aider à identifier ces éléments dans le texte.
Informations pour LUIS : https://docs.microsoft.com/fr-fr/azure/cognitive-services/luis/

Le chatbot devra également : 
1) identifier les éléments manquants et poser à l'utilisateur les questions pertinentes afin de bien comprendre la demande. 
2) Reformuler la demande de l'utilisateur.
3) Demander à l'utilisateur de valider les informations.

Le MS SDK sera utilisé pour aider à atteindre ces objectifs : 
https://docs.microsoft.com/fr-fr/azure/bot-service/index-bf-sdk?view=azure-bot-service-4.0

Nous suivrons également les performances du chatbot en fournissant :
1) un graphique des performances du chatbot créé à partir des logs des données de trace.
2) Une alerte lorsque certaines conditions de performance sont remplies. 

Les outils d'Application Insights seront utilisés pour aider à atteindre ces objectifs : https://docs.microsoft.com/fr-fr/azure/azure-monitor/app/app-insights-overview
