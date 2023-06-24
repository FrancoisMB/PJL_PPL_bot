# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 17:41:51 2021


http://www2.assemblee-nationale.fr/documents/liste/(type)/depots
http://www.senat.fr/dossiers-legislatifs/textes-recents.html


@author: Francois
"""

     
# on initie un DF      num text | date d'ajout | tweeté 
# on charge le csv de mémoire dedans
# on ajoute une nouvelle colonne vide flag_vu
    # qui contiendra le fait que les lignes dans le DF existent aussi dans la page
# on scrap la page de l'AN
# pour chaque entrée dans la page de l'AN
    # on regarde si c'est dans le DF
        # Non : c'est pas dans le DF on le met dedans (avec la date d'ajout ?) et on on met le flag "tweeté" = 0 et vu = 1
        # Oui : on set le flag vu = 1, et on récupère l'info du flag "tweeté"
    # si flag tweeté = 1
        # continue à la next itération de la boucle
    # si on est là c'est que ça a pas été tweeté
    # du coup on scrape la page du texte lui même
    # si on trouve "Document non encore publié"
        # continue à la next itération de la boucle
    # sinon, c'est que le texte est publié
    # donc on tweete
    # et on set flag tweeté = 1
# on order le DF en fonction de la date d'ajout, du plus récent au plus ancien EN FAIT NON
# dans le DF, on supprime les lignes où vu = 0
# on enregistre le DF qui reste
    
# TODO : implémenter le truc des tours de boucle (cf script amendements gouv)
# TODO : dès qu'il repère une erreur à l'une des tours de boucle, créer un 
#        fichier de log_date_tour_de_boucle, et y inscrire toutes les erreurs 
#        et variables de ce tour de boucle (et ne plus les print)
#        + à la toute fin, si un fichier a été créé, print un message pour le dire
    
if __name__ == "__main__":
    
    from pathlib import Path
    from lxml import html
    import os, time, tweepy, requests, re, pandas
    
    # set le dossier de travail à l'endroit où se trouve 
    path_wd = r"D:\Code\Code_Python\scrapper_textes_deposes_parlement"
    os.chdir(path_wd)
    
    # 2) initier des fichiers
    if not os.path.exists('date_dernier_run.txt'):
        Path('date_dernier_run.txt').touch()
    f = open("date_dernier_run.txt", "r")
    date_dernier_run = f.read()
    f.close()
    print("date_dernier_run =", date_dernier_run)
    
    # connexion à twitter
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_secret = ""
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    
    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")
    
    tweet_size = 280 - 24
    
    def formatage_texte(input_text):
        if len(input_text) > tweet_size:
            input_text = input_text.replace('Proposition de loi organique', 'PPLO')
            input_text = input_text.replace('proposition de loi organique', 'PPLO')
            input_text = input_text.replace('Projet de loi organique', '⚠️ PJLO')
            input_text = input_text.replace('projet de loi organique', '⚠️ PJLO')
            input_text = input_text.replace('Proposition de loi constitutionnelle', 'PPLC')
            input_text = input_text.replace('proposition de loi constitutionnelle', 'PPLC')
            input_text = input_text.replace('Projet de loi constitutionnelle', '⚠️ PJLC')
            input_text = input_text.replace('projet de loi constitutionnelle', '⚠️ PJLC')
    
        input_text = input_text.replace('Projet de loi de finances rectificative', '⚠️ #PLFR')
        input_text = input_text.replace('projet de loi de finances rectificative', '⚠️ #PLFR')
        input_text = input_text.replace('Projet de loi de finances', '⚠️ #PLF')
        input_text = input_text.replace('projet de loi de finances', '⚠️ #PLF')
        
        input_text = input_text.replace('Projet de loi de financement de la sécurité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la sécurité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('Projet de loi de financement de la sécurite sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la sécurite sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('Projet de loi de financement de la securité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la securité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('Projet de loi de financement de la securite sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la securite sociale', '⚠️ #PLFSS')
    
        input_text = input_text.replace('Projet de loi de financement de la Sécurité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la Sécurité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('Projet de loi de financement de la Sécurite sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la Sécurite sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('Projet de loi de financement de la Securité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la Securité sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('Projet de loi de financement de la Securite sociale', '⚠️ #PLFSS')
        input_text = input_text.replace('projet de loi de financement de la Securite sociale', '⚠️ #PLFSS')
    
        input_text = input_text.replace('Projet de loi de financement rectificative de la sécurité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la sécurité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('Projet de loi de financement rectificative de la sécurite sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la sécurite sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('Projet de loi de financement rectificative de la securité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la securité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('Projet de loi de financement rectificative de la securite sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la securite sociale', '⚠️ #PLFRSS')
    
        input_text = input_text.replace('Projet de loi de financement rectificative de la Sécurité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la Sécurité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('Projet de loi de financement rectificative de la Sécurite sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la Sécurite sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('Projet de loi de financement rectificative de la Securité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la Securité sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('Projet de loi de financement rectificative de la Securite sociale', '⚠️ #PLFRSS')
        input_text = input_text.replace('projet de loi de financement rectificative de la Securite sociale', '⚠️ #PLFRSS')
     
        input_text = input_text.replace('#PLFR', '#PLFℝ') # change le R en un R spécial un peu plus visible, qui est admis en hashtag twitter comme un R classique
    
        input_text = input_text.replace('Proposition de loi', 'PPL')
        input_text = input_text.replace('proposition de loi', 'PPL')
        input_text = input_text.replace('Projet de loi', '⚠️ PJL')    
        input_text = input_text.replace('projet de loi', '⚠️ PJL') 
        input_text = input_text.replace('Proposition de résolution', 'PPR')
        input_text = input_text.replace('proposition de résolution', 'PPR')
        input_text = input_text.replace('Proposition de resolution', 'PPR')
        input_text = input_text.replace('proposition de resolution', 'PPR')    
        input_text = input_text.replace('et plusieurs de ses collègues', '')
        input_text = input_text.replace('et plusieurs de ses collegues', '')
        input_text = input_text.replace('et plusieurs de leurs collègues', '')
        input_text = input_text.replace('et plusieurs de leurs collegues', '')
        input_text = input_text.replace(', plusieurs de ses collègues', '')
        input_text = input_text.replace(', plusieurs de ses collegues', '')
        input_text = input_text.replace(', plusieurs de leurs collègues', '')
        input_text = input_text.replace(', plusieurs de leurs collegues', '')
        
        input_text = input_text.replace('après engagement de la procédure accélérée', '')
        input_text = input_text.replace('et plusieurs de ses collegues', '')
        input_text = input_text.replace('et plusieurs de ses collègues', '')
        input_text = input_text.replace('et plusieurs de leurs collègues', '')
        input_text = input_text.replace('et plusieurs de leurs collegues', '')
        
        input_text = ' '.join(input_text.split())
        input_text = input_text.replace(' ,', ',')
        input_text = input_text.replace(',,,', ',')
        input_text = input_text.replace(',,', ',')
        input_text = ' '.join(input_text.split())
    
        if len(input_text) <= tweet_size:
            return input_text +" "
        else:
            return input_text[:tweet_size-3]+"... "
        
    #%%
    
    send_to_twitter = 1
    enregistrer_quand_meme = 1
    verbose = 0
    
    scrap_AN = 1
    nb_de_textes_a_scrapper = 149
    
    scrap_Senat = 1
    nb_de_dates_a_scrapper = 25
    
    
    while True:
        pass
    
        try:
        #%%
    
            # initialisation du fichier AN
                    
            nom_fichier_AN = "v4_dernier_numero_texte_depose_AN.csv"
            
            try:
                df_AN = pandas.read_csv(nom_fichier_AN, index_col=0)
            except:
                print("PB dans l'import du précédent fichier AN, un nouveau a du être recréé")
                df_AN = pandas.DataFrame(columns=["flag_tweeted"])
            
            # on ajoute une nouvelle colonne vide flag_vu
                # qui contiendra le fait que les lignes dans le df_AN existent aussi dans la page
            df_AN['flag_vu'] = 0
            
            
            # initialisation du fichier Sénat
            
            nom_fichier_S = "v4_dernier_numero_texte_depose_S.csv"
            
            try:
                df_S = pandas.read_csv(nom_fichier_S, index_col=0)
            except:
                print("PB dans l'import du précédent fichier AN, un nouveau a du être recréé")
                df_S = pandas.DataFrame(columns=["flag_tweeted"])
            
            # on ajoute une nouvelle colonne vide flag_vu
                # qui contiendra le fait que les lignes dans le df_S existent aussi dans la page
            df_S['flag_vu'] = 0   
            
            
            #%% 
            if scrap_AN:
                # on scrap la page de l'AN
                # balises pour le texte :
                     # /html/body/div[1]/div[3]/div/div/section/div/article/div/div[2]/div[2]/ul/li[1]/p/text()
                     # /html/body/div[1]/div[3]/div/div/section/div/article/div/div[2]/div[2]/ul/li[2]/p/text()
                 
                 # balise qu'on veut récupérer pour les liens derrière "dossier législatif" : .enligne li a    + prendre le premier des deux éléments
                     #/html/body/div[1]/div[3]/div/div/section/div/article/div/div[2]/div[2]/ul/li[2]/ul/li[2]/a
                     #/html/body/div[1]/div[3]/div/div/section/div/article/div/div[2]/div[2]/ul/li[3]/ul/li[2]/a
                 
                url_AN = "http://www2.assemblee-nationale.fr/documents/liste/(type)/depots"
                page_AN = requests.get(url_AN)
                tree = html.fromstring(page_AN.content)
                
                i = 1
                
                nb_de_textes_a_scrapper = nb_de_textes_a_scrapper
                while i <= nb_de_textes_a_scrapper: # pour chaque entrée dans la page de la liste des textes de l'AN
                    i = i+1
                    try: # on récupère son numéro de texte
                        base_xpath = '/html/body/div[1]/div[2]/div/div/section/div/article/div/div[2]/div[2]/ul/li['+ str(i) +']'
                        numero_du_texte = str(tree.xpath(base_xpath+'/h3/text()')[0])
                        numero_du_texte = numero_du_texte.split("N°",1)[1] #permet de ne récupérer que ce qui est après "- N° "
                        numero_du_texte = numero_du_texte.replace(u'\xa0', u'')
                        #print(numero_du_texte)
                    except:
                        print("AN erreur pour récupérer numéro du texte à la boucle n°" + str(i-1))
                        print("")
                        continue
                    
                    #numero_du_texte = "4723"
                    if not(numero_du_texte in df_AN.index):  # on regarde si son numéro de texte est dans le df_AN
                        # Non : c'est pas dans le df_AN on le met dedans (avec la date d'ajout ?) et on on met le flag "tweeté" = 0 et vu = 1
                        #df_AN = df_AN.append(pandas.Series({"flag_tweeted" : 0, "flag_vu" : 1}, name=numero_du_texte)) # TODO : si la ligne suivante ne produit pas de bugs pendant suffisamment de temps, alors celle ci peut être supprimée (car deprecated)
                        df_AN = pandas.concat([df_AN, pandas.Series({"flag_tweeted" : 0, "flag_vu" : 1}, name=numero_du_texte)])

                    else:
                        # Oui : on set le flag vu = 1, et on récupère l'info du flag "tweeté"
                        df_AN.at[numero_du_texte,"flag_vu"] = 1
                        if df_AN.at[numero_du_texte, "flag_tweeted"] == 1: # si flag tweeté = 1, pas besoin de traiter, on continue à la next itération de la boucle
                            if verbose:print(numero_du_texte, "\t \t \t \t \t \t déjà tweeté")
                            continue
                
                    # si on arrive là c'est soit que c'est un nouveau texte dans la liste
                    # soit que c'est un texte déjà vu dans la liste, mais pas encore tweeté
                
                
                    # du coup on scrape la page du texte lui même
                
                    try:
                        lien_vers_dossier = str(tree.xpath(base_xpath+'/ul/li[2]/a')[0].attrib["href"])
                        lien_vers_texte = str(tree.xpath(base_xpath+'/ul/li[3]/a')[0].attrib["href"])
                    except:
                        # si on est ici, c'est qu'il n'y a pas la mention "mis en ligne le XXX" dans la liste, et donc que 2 éléments et pas 3 sur la ligne
                        # et donc la recherche avec le xpath de "lien_vers_texte" ci dessus renvoie une erreur "list index out of range"                   
                        if verbose:print(numero_du_texte, "\t \t \t \t \t \t doc non pub")
                        continue
    
                    try :
                        page_texte_AN = requests.get(lien_vers_texte)
                        # si on trouve "Document non encore publié", on passe au prochain texte de la liste
                        if "Document non encore publié" in page_texte_AN.text:    
                            if 1:print(numero_du_texte, "\t \t \t \t \t \t doc non pub type 2 c chelou")
                            continue
                    except:
                        # là j'ai voulu faire une vérif que dans la page du texte, il n'y avait pas "Document non encore publié
                        # mais ça a raté, jsais pas, ptet timeout
                        # osef, on tweete
                        pass
                
                    # si on est là, normalement c'est que le texte est publié donc on tweete
                    try:
                        intitule_du_texte = str(tree.xpath(base_xpath+'/p/text()')[0])
                        #print(intitule_du_texte)
                    except:
                        print("AN erreur pour récupérer intitulé du texte", numero_du_texte)
                        print("")
                        continue  # permet de ne pas mettre un truc sans intitule_du_texte dans liste_textes
                        
                    intitule_du_texte = formatage_texte(intitule_du_texte) # transforme "projet de loi" en "PJL" etcaetera
                
                    texte_du_tweet = intitule_du_texte + lien_vers_texte
                
                    if send_to_twitter == True:
                        try:
                            tweeted = api.update_status(texte_du_tweet)
                        except Exception as err:
                            if err.args[0] == '403 Forbidden\n187 - Status is a duplicate.':
                                df_AN.at[numero_du_texte,"flag_tweeted"] = 1
                            print("Erreur lors du tweet de", texte_du_tweet)
                            print(err)
                            print("")
                            continue
                    # et on set flag tweeté = 1
                    df_AN.at[numero_du_texte,"flag_tweeted"] = 1
                    print("AN -", texte_du_tweet)
                    print(" ")
                
                if enregistrer_quand_meme:
                    # dans le df_AN, on supprime les lignes où vu = 0
                    df_AN = df_AN.drop(df_AN[df_AN.flag_vu == 0].index)
                    
                    # on enregistre le df_AN qui reste
                    df_AN.to_csv(nom_fichier_AN, columns=["flag_tweeted"])
    
    
    
    
    
    
    
            #%%
            
            if scrap_Senat:
    
                # 4) b) scrapper la page du Sénat (pas de limite sur le nombre d'éléments, il y a les 12 derniers mois)
                    # s'il n'y a qu'un texte à une date, le xpath prend la forme : 
                    # /html/body/div[1]/div/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[1]/ul/li/a
                    # s'il y en a plusieurs, les xpath prennent la forme : 
                    # /html/body/div[1]/div/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[4]/ul/li[1]/a
                    # /html/body/div[1]/div/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[4]/ul/li[2]/a
                    # /html/body/div[1]/div/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[4]/ul/li[3]/a
                    # /html/body/div[1]/div/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li[5]/ul/li/a
                 
                url_Senat = "http://www.senat.fr/dossiers-legislatifs/textes-recents.html"
                page_Senat = requests.get(url_Senat)
                tree = html.fromstring(page_Senat.content)
                
                i = 1
                
                nb_de_dates_a_scrapper = nb_de_dates_a_scrapper
                while i <= nb_de_dates_a_scrapper:
                    i+=1
                    liste_intitule_des_textes = tree.xpath('/html/body/div[1]/div/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/ul/li['+ str(i) +']/ul/li/a')
                    for j in range(len(liste_intitule_des_textes)):
                        time.sleep(0.01)
                        
                        try:
                            intitule_du_texte = liste_intitule_des_textes[j].text
                            #print(liste_intitule_des_textes[j].text)
                        except:
                            print("S erreur pour récupérer intitulé du texte à la", str(i-1)+"ème date, texte n°" + str(j+1))
                            # nb_de_dates_a_scrapper = nb_de_dates_a_scrapper + 1 # ça ça générait un loop infini à l'AN, au Sénat je sais pas, je crois pas, mais dans le doute je grey out
                            continue
                        
                        try:
                            numero_du_texte = liste_intitule_des_textes[j].attrib["href"]
                            lien_vers_dossier = "http://www.senat.fr" + numero_du_texte
                            #print(lien_vers_dossier)
                            numero_du_texte = numero_du_texte[20:-5]
                        except:
                            print("S erreur pour récupérer lien", intitule_du_texte)
                            print(" ")
                            # nb_de_dates_a_scrapper = nb_de_dates_a_scrapper + 1 # ça ça générait un loop infini à l'AN, au Sénat je sais pas, je crois pas, mais dans le doute je grey out
                            continue  
                           
                        #numero_du_texte = "4723"
                        if not(numero_du_texte in df_S.index):  # on regarde si son numéro de texte est dans le df_S
                            # Non : c'est pas dans le df_S on le met dedans (avec la date d'ajout ?) et on on met le flag "tweeté" = 0 et vu = 1
                            #df_S = df_S.append(pandas.Series({"flag_tweeted" : 0, "flag_vu" : 1}, name=numero_du_texte)) # TODO : si la ligne suivante ne produit pas de bugs pendant suffisamment de temps, alors celle ci peut être supprimée (car deprecated)
                            df_S = pandas.concat([df_S, pandas.Series({"flag_tweeted" : 0, "flag_vu" : 1}, name=numero_du_texte)])
               
                        else:
                            # Oui : on set le flag vu = 1, et on récupère l'info du flag "tweeté"
                            df_S.at[numero_du_texte,"flag_vu"] = 1
                            if df_S.at[numero_du_texte, "flag_tweeted"] == 1: # si flag tweeté = 1, pas besoin de traiter, on continue à la next itération de la boucle
                                if verbose:print(numero_du_texte, "\t \t \t \t \t \t déjà tweeté")
                                continue
                
                        # si on arrive là c'est soit que c'est un nouveau texte dans la liste
                        # soit que c'est un texte déjà vu dans la liste, mais pas encore tweeté
                    
                        # du coup on scrape la page du DOSSIER pour récupérer le dernier état du texte
        
        
                        # lien_vers_dossier = "http://www.senat.fr/dossier-legislatif/ppl19-629.html" # ici, dernier texte = commission AN
        
                        # lien_vers_dossier = "http://www.senat.fr/dossier-legislatif/pjl20-764.html" # ici, dernier texte = commission Sénat
        
                        # lien_vers_dossier = "http://www.senat.fr/dossier-legislatif/ppl20-780.html" # ici, CMP
        
                        # lien_vers_dossier = "http://www.senat.fr/dossier-legislatif/ppl21-183.html" # ici, pas de texte publié
        
                        try:
                            page_dossier = requests.get(lien_vers_dossier)            
                            page_dossier = ' '.join(page_dossier.text.split())
                            
                            # A FAIRE:
                            # trouver l'occurrence la plus en bas de "Texte" (avec un lien, parce qu'il existe le mot texte sans lien) ou de "Texte de la commission"
                            # regarder le href, si c'est site de l'AN
                                # continue (on s'arrête)
                            # si c'est site du Sénat, récupérer le href, qui est le href de la dernière version du texte 
                                # (qu'on ne mettra pas dans le df_S, on fonctionne qu'avec le numero d'origine du texte, qui est celui du dossier législatif)
                            # parfois ya pas de lien, comme ici, pour l'instant : http://www.senat.fr/dossier-legislatif/ppl21-181.html
                            # dans ce cas => continue
                            
                            # NB : je ne sais pas ce qu'il se passe en cas de CMP, traiter aussi ce cas
        
        
        
                            liste_start_mot_texte = [m.start() for m in re.finditer('Texte</a>', page_dossier)] # retourne toutes les positions de la première lettre des occurrences du mot "Texte"
                            liste_start_mot_texte_commission = [m.start() for m in re.finditer('Texte de la commission</a>', page_dossier)] # retourne toutes les positions de la première lettre des occurrences du mot "Texte"
        
                            # le bloc try/except ci-dessous sert à gérer le cas où il y a "Texte n°" sur la page, sans lien : texte pas encore publié
                            # le bloc pourrait PEUT ETRE être simplifié en ajoutant ça au dessus :
                            # liste_start_mot_texte_n = [m.start() for m in re.finditer('Texte n°', page_dossier)] # retourne toutes les positions de la première lettre des occurrences du mot "Texte"
                            # en mettant dans le try ci dessous :
                            # max_des_deux = max(liste_start_mot_texte_commission + liste_start_mot_texte + liste_start_mot_texte_n)
                            # et ce serait ensuite géré comme troisième cas du IF/ELIF/ELSE qui suit.  Pas sûr. A voir...
                            try:
                                max_des_deux = max(liste_start_mot_texte_commission + liste_start_mot_texte) # position du dernier endroit où il a "Texte</a>" ou "Texte de la commission</a>"
                            except ValueError as e:
                                if str(e) == "max() arg is an empty sequence": # signifie que les deux listes étaient vides
                                    # du coup par curiosité, je teste qu'on a bien écrit "Texte n° XXX" sans lien
                                    start_pos = [m.start() for m in re.finditer('Texte', page_dossier)][-1]
                                    if "<li>Texte n°" in page_dossier[start_pos-4:start_pos+8]:
                                        # le pattern ressemble bien à celui d'un texte non encore publié
                                        if verbose:print(numero_du_texte, "\t \t \t \t \t \t non pub")
                                        # donc on peut partir
                                        continue
                                        # par acquis de conscience, je pourrais vérifier que le lien vers le texte donne bien 404...
                                    elif "<li>Texte retiré" in page_dossier[start_pos-4:start_pos+12]:
                                        # traiter le cas d'un texte retiré comme celui ci : http://www.senat.fr/dossier-legislatif/ppl21-906.html
                                        if verbose:print("texte retiré, voilà le lien vers le dossier législatif :", lien_vers_dossier)
                                        continue
                                    else:
                                        print("c'est chelou, ni 'Texte</a>' ni 'Texte de la commission</a>' n'ont été trouvés, ni 'Texte n°' sans lien")
                                        print("voilà le lien vers le dossier législatif :", lien_vers_dossier)
                                        continue
        
                            borne_arriere = 26 # choisi un peu au pif, de manière à capturer le texte "Texte de la commission</a>"
                            
                            # SI le lien est un lien du Sénat, il fera toujours 30 caractères avant le mot "Texte" : <a href="/leg/ppl21-151.html">
                            # Si le lien est de l'AN, sa taille peut varier
                            borne_avant_test_Senat = -30
                            borne_avant_test_AN = -100
                            
                            if "href='/leg/" in page_dossier[ max_des_deux + borne_avant_test_Senat : max_des_deux + borne_arriere ]:
                                # si on est là, c'est qu'on a un lien Sénat
                                borne_avant = -21
                                borne_arriere = -2
                                lien_vers_texte = "http://www.senat.fr" + page_dossier[ max_des_deux + borne_avant : max_des_deux + borne_arriere ]
                                
                            elif 'nationale.fr' in page_dossier[ max_des_deux + borne_avant_test_AN : max_des_deux + borne_arriere ] :
                                # La dernière version du texte est un texte de l'AN, on peut arrêter et passer au texte suivant
                                if verbose:print(numero_du_texte, "\t \t \t \t \t \t lien AN")
                                
                                continue
                            else: # cas où ya rien
                                print("c'est chelou, 'Texte</a>' ou 'Texte de la commission</a>' a bien été trouvé")
                                print("mais on a pas trouvé de lien AN ou Sénat devant")
                                print("voilà le lien vers le dossier législatif :", lien_vers_dossier)
                                continue
                      
                                
                        except Exception as erreur:
                            print("S erreur pour récupérer, dans le dossier législatif, le lien vers la dernière version du texte", lien_vers_dossier)
                            print("print de l'erreur :")
                            print(erreur)
                            print(" ")
                            continue
                        
                            
                        # lien_vers_texte = "http://www.senat.fr/leg/ppl21-181.html"   # pour les tests
        
                        # et ensuite on scrape la page du texte lui même
                        page_texte_S = requests.get(lien_vers_texte)            
                        # si on trouve la phrase ci-dessous, c'est qu'on est sur la page 404 du Sénat
                        if "une erreur du Webmestre dans un lien" in page_texte_S.text:    
                            if verbose:print(numero_du_texte, "\t \t \t \t \t \t doc non pub")
                            continue # donc on peut passer au prochain texte
                        
                        # sinon, c'est que le texte est publié donc on tweete
                        intitule_du_texte = formatage_texte(intitule_du_texte) # transforme "projet de loi" en "PJL" etcaetera
                
                        texte_du_tweet = intitule_du_texte + lien_vers_texte
                
                        if send_to_twitter == True:
                            try:
                                tweeted = api.update_status(texte_du_tweet)
                            except Exception as err:
                                if err.args[0] == '403 Forbidden\n187 - Status is a duplicate.':
                                    df_AN.at[numero_du_texte,"flag_tweeted"] = 1
                                print("Erreur lors du tweet de", texte_du_tweet)
                                print(err)
                                print("")
                                continue
                        # et on set flag tweeté = 1
                        df_S.at[numero_du_texte,"flag_tweeted"] = 1
                        print("S -", texte_du_tweet)
                        print(" ")
        
                if enregistrer_quand_meme:
                    # dans le df_S, on supprime les lignes où vu = 0
                    df_S = df_S.drop(df_S[df_S.flag_vu == 0].index)
                    
                    # on enregistre le df_S qui reste
                    df_S.to_csv(nom_fichier_S, columns=["flag_tweeted"])    
        
    #%%
            print(".", end="")            
            if send_to_twitter == 0:
                break
            time.sleep(120)             
                
        except Exception as err:
            print(err)
            time.sleep(60) 
    
    
    
    