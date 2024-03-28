

# Chemin pour acceder au fichier texte
path_to_file = "D:/2/Fichier/ITEL.txt"

# Ouvrir et lire le fichier texte
fichier = open(path_to_file,"r")
texte = fichier.read()




# STOCKER LES DOMAINS AVEC LEURS TYPES
# EXEMPLE : [['ANEXOFIS','CHAR(8)'],['NOCC','SMALLINT'],..,[....]]

domain = []

# Compter le nombre de domain different dans le texte
n = texte.count("domain")

# Tant que on a pas eu tous les domains
while len(domain) != n:
    for i in range(len(texte)-6):
        if texte[i:i+6] == "domain":

            # Stocker nom de type dans la variable type_nom comme ANEXOFIS
            indice_nom = texte[i+7::].index('\n')
            type_name = texte[i+7:i+7+indice_nom]

            # Stocker le type correspondant dans la variable type_var comme CHAR(8)
            indice_debut = i + 9 + len(type_name)
            if 'comment' in texte[indice_debut:indice_debut+40]:
                indice_fin = indice_debut + texte[indice_debut::].index('\n')
            else:
                indice_fin = indice_debut + texte[indice_debut::].index(';')
            type_var = texte[indice_debut:indice_fin].replace(' ','')


            j = 0
            s = 0
            test = 0
            while s != 1:
                if texte[i+j:i+j+18] == 'comment is \n      ':
                    s+=1
                    test = 1
                if texte[i+j] == ';':
                    s+=1
                else:
                    j+=1

            if test == 1:
                ind_debut_comment = i+j+17
                k = 0
                while texte[ind_debut_comment+k] != ';':
                    k+=1
                ind_fin_comment = ind_debut_comment+k
                comment_domain = texte[ind_debut_comment:ind_fin_comment]
            else:
                comment_domain = ''



            # Stocker dans une liste [['A','char(8)'],['B',SMALLINT]]
            domain.append([type_name,type_var,comment_domain])






# Indice ou les create table commencent :
indice_table_debut = texte.index('create table')


# Indice ou les create table finissent
if 'alter table' in texte[indice_table_debut::]:
    indice_alter_table = texte[indice_table_debut::].index('alter table')
    indice_table_fin = min(texte[indice_table_debut::].index('Index Definitions'),indice_alter_table)
else:
    indice_table_fin = texte[indice_table_debut::].index('Index Definitions')
    j = 0
    indice = indice_table_fin+indice_table_debut
    while texte[indice-j-6:indice-j] != 'commit':
        j+=1
    indice_table_fin = indice_table_fin-j-6






# On extrait du texte seulement la partie contenant les create table
text_table = texte[indice_table_debut:indice_table_fin + indice_table_debut]




# On modifie le texte
i = 0
while i < len(text_table):
    if text_table[i] == ',' or text_table[i:i+2] in [');',')\n'] or text_table[i:i+10] == '\n        c':
        j = 0
        while text_table[i-j] != ' ':
            j+=1
        indice_espace = i-j
        mot = text_table[i-j+1:i]
        for k in range(len(domain)):
            if domain[k][0] == mot:
                t1 = text_table[:i-j]
                if domain[k][1] == 'DATEVMS':
                    t2 = text_table[i-j:].replace(mot,'DATE',1)
                else:
                    t2 = text_table[i-j:].replace(mot,domain[k][1],1)
                text_table = t1 + t2

    i+=1




# On transforme CHAR en VARCHAR2 sauf CHAR(1)
i = 0
while i < len(text_table):
    if text_table[i:i+6] == 'CHAR (':
        if text_table[i+6:i+8] != '1)':
            t = text_table[i:i+6].replace('CHAR ','VARCHAR2')
            text_table = text_table[:i] + t + text_table[i+6:]
    elif text_table[i:i+5] == 'CHAR(' and text_table[i-3:i] != 'VAR':
        if text_table[i+5:i+7] != '1)':
            t = text_table[i:i+5].replace('CHAR','VARCHAR2')
            text_table = text_table[:i] + t + text_table[i+5:]
    i+=1





# Mettre les commentaires des tables en bas de chaque table
i = 0
while i < len(text_table):
    if text_table[i:i+16] == ')\n    comment is':
        j = 0
        while text_table[i+16+j] != ';':
            j+=1
        comment = text_table[i+16:i+17+j]
        j=0
        while text_table[i-j-11:i-j] != 'reate table':
            j+=1
        k = 0
        while text_table[i-j+k:i-j+k+2] != ' (':
            k+=1
        table_name = text_table[i-j+1:i-j+k]
        text_table =text_table[:i+1]+';\n\n'+'comment on table '+table_name+' is '+text_table[i+16:]
    i+=1





i = 0
while i < len(text_table):
    if text_table[i:i+18] == '        comment is':
        j = 0
        while text_table[i+j+18] not in [',',')']:
            j+=1
        commentaire = text_table[i+18:i+j+18]
        j = 0
        while text_table[i-j] != ',':
            j+=1
        k = 0
        while text_table[i-k-2:i-k] != ' (':
            k+=1
        j = min(j,k)
        ind_deb_colonne = []
        k = 0
        while text_table[i-j+k+2] != '\n':
            if text_table[i-j+k] == ' ':
                if text_table[i-j+k+1] in '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    ind_deb_colonne.append(i-j+k+1)
                if text_table[i-j+k-1] in '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    ind_fin_colonne = i-j+k
            k+=1
        if len(ind_deb_colonne) != 0:
            column_name = text_table[ind_deb_colonne[0]:ind_fin_colonne]



        # Determiner nom table pour colonne correspondante
        j=0
        while text_table[i-j-11:i-j] != 'reate table':
            j+=1
        k = 0
        while text_table[i-j+k:i-j+k+2] != ' (':
            k+=1
        table_name_corresp = text_table[i-j+1:i-j+k]



        # Mettre commentaire colonne en bas
        en_bas = 'comment on column '+table_name_corresp+'.'+column_name+' is '+ commentaire+';\n\n'
        j = 0
        while text_table[i+j:i+j+12] != 'create table':
            j+=1
        text_table = text_table[:i+j]+en_bas+text_table[i+j:]


    i+=1





# Effacer comment is colonne dans les create table
i = 0
while i < len(text_table):
    if text_table[i:i+18] == '        comment is':
        j = 0
        while text_table[i+18+j] not in [',',';']:
            j+=1
        if text_table[i+18+j] == ',':
            text_table = text_table[:i-1] + text_table[i+18+j:]
        else:
            text_table = text_table[:i-1] + text_table[i+18+j:]
    i+=1





i = 0
while i < len(text_table)-4:
    if text_table[i:i+4] == '    ' and text_table[i+4] not in ['/',"'"] and text_table[i+4:i+6] != 'co' and text_table[i-1] == '\n':
        if text_table[i+4] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':

            j = 0
            while text_table[i+j+4] not in [' ','\n']:
                j+=1
            nom = text_table[i+4:i+j+4]


            for k in range(len(domain)):
                if domain[k][0] == nom:
                    commentaire = domain[k][2]



            if 'VARCHAR' not in nom:
                # Determiner nom table pour colonne correspondante
                j=0
                while text_table[i-j-11:i-j] != 'reate table':
                    j+=1
                s = 0
                while text_table[i-j+s:i-j+s+2] != ' (':
                    s+=1
                table_name_corresp = text_table[i-j+1:i-j+s]

                # Mettre commentaire colonne en bas
                en_bas = 'comment on column '+table_name_corresp+'.'+nom+' is '+ commentaire+';\n\n'


                j = 0
                k= 0
                test_2 = 0
                while k != 1:
                    if 'create table' not in text_table[i+j:]:
                        t = 0
                        while text_table[i+j+t:i+j+t+16] != 'comment on table':
                            t+=1
                        e = 0
                        while text_table[i+j+t+e+16] != ';':
                            e+=1
                        Indice = i+j+t+e+17
                        test_2 = 1
                        k=1
                    elif text_table[i+j:i+j+12] == 'create table':
                        Indice = i+j
                        k=1
                    else:
                        j+=1

                if commentaire != '':
                    if test_2 ==0:

                        text_table = text_table[:Indice]+en_bas+text_table[Indice:]
                    else:
                        print(2)
                        text_table = text_table[:Indice]+'\n\n'+en_bas+text_table[Indice:]

    i+=1





i = 0
while i < len(text_table):
    if text_table[i:i+12] == 'create table':
        text_table = text_table[:i] + '\n\n' + text_table[i:]
        i+=12
    i+=1




# On concatene tous les textes
texte_fin = texte[:indice_table_debut]+ text_table + texte[indice_table_fin+indice_table_debut:-1]



# On supprime les commit work
texte_fin = texte_fin.replace('commit work;\n','')




# Retirer les set transaction
i = 0
while i < len(texte_fin):
    if texte_fin[i:i+15] == 'set transaction':
        j = 0
        while texte_fin[i+15+j] != ';':
            j+=1
        texte_fin = texte_fin[:i] + texte_fin[i+16+j:]
    i+=1




# Supprimer les type is dans les create index
i = 0
while i < len(texte_fin):
    if texte_fin[i:i+7] == 'type is':
        j = 0
        while texte_fin[i+7+j] != ';':
            j+=1
        texte_fin = texte_fin[:i] + texte_fin[i+7+j:]
    i+=1





# Creer nouveau fichier texte avec les changements
# IL FAUT MODIFIER emplacement du fichier
path_file = 'D:/2/fin.txt'
with open(path_file, "w") as f:
    print(texte_fin, file = f)




# FERMER LES FICHIERS TEXTES
fichier.close()
f.close()
