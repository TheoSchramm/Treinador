
import discord
from discord.ext import commands
from settings import*
import random,json,os,threading
from datetime import datetime

client = commands.Bot(PREFIX, case_insensitive=True, help_command=None)

##### ON READY #####
@client.event
async def on_ready():
  print(f'Bot inicializado com sucesso! ({client.user})')
  print('----------------------------------------------')
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="NBA"))

##### AJUDA #####
@client.command(aliases=['ajuda'])
async def help(ctx):
  registrar(ctx)
  await ctx.send('''```
Summon:
  · Use $ba para revelar 1 jogador de basquete aleatório.
  · Use $mu para ver se você pode contratar no momento.
  · Use $trade @Alguém para trocar seus jogadores com outro gerente.

Perfil:
  · Use $mma @Alguém para ver os jogadores de alguém.
  · Use $im <nome do jogador> para visualizar o contrato do jogador.
  · Use $bal para ver o saldo de sua carteira.

Misc:
  · Use $dk para ganhar uma grana.
  · Use $pix @Alguém <quantia> para pagar outro gerente.
  · Use ajuda para ver esta mensagem novamente.
```''')

#· Use **$set #nome-do-canal-de-texto** para definir o canal que vou funcionar###################################################################################################

@client.command()
async def ba(ctx): 
    registrar(ctx)
    
    if os.path.isfile("roster.json"):
        with open("roster.json", "r") as fp:
                summon_data = json.load(fp)
        summon_key  = str(random.randint(1,len(summon_data)))
        summon = summon_data[summon_key]

    ##### JSON START #####
    if os.path.isfile("users.json"):
        with open("users.json", "r") as fp:
          user_data = json.load(fp)
        if user_data[f"{ctx.author.id}"]["rolls"] > 0:
          with open("users.json", "w+") as fp:
            user_data[f"{ctx.author.id}"]["rolls"] -= 1
            json.dump(user_data, fp, indent=4)

            ############### Summon c/ claim
          if summon['gerente'] == 'sem_gerente':
            embedVar = discord.Embed(title=summon["nome"], description=f'_{summon["time"]}_\n_Camisa #{summon["camisa"]}_\nReaja com qualquer emote para **contratar** o jogador!', color = discord.Colour.random())
            embedVar.set_image(url=summon['url'])

                # Aviso dos rolls
            if user_data[f"{ctx.author.id}"]["rolls"] == 0:
              embedVar.set_footer(text=f"⚠️  ACABARAM OS ROLLS  ⚠️")
            elif user_data[f"{ctx.author.id}"]["rolls"] <= 3:
              embedVar.set_footer(text=f"⚠️  {user_data[f'{ctx.author.id}']['rolls']} ROLLS RESTANTES  ⚠️")
        
            msg = await ctx.channel.send(embed=embedVar)
            await msg.add_reaction('🏀')

            # Criação da reação + verificação 
            def check(reaction, user):
              return str(reaction.emoji) == str(reaction.emoji) and user != client.user and msg.id == reaction.message.id and user_data[f"{user.id}"]["claim"] > 0
                
            try:
              reaction, user = await client.wait_for('reaction_add', timeout=60, check=check)
            except:
              pass
              #await ctx.send(f'Calma meu patrão. Para este servidor, você pode **contratar** uma vez a cada 3 horas. {msg_claim_reset}')
            else:
              user_data[f"{user.id}"]["claim"] -= 1
              summon["gerente"] = user.id
              await ctx.send(f':basketball:  **{user.name}** agora possui o contrato de **{summon["nome"]}**!  :basketball:')



        ############### Summon c/ grana
          else:
            username = await client.fetch_user(summon["gerente"])
            embedVar = discord.Embed(title=summon["nome"],description=f'_{summon["time"]}_\n_Camisa #{summon["camisa"]}_\nReaja com qualquer emote para **cobrar** o jogador!',color = discord.Colour.random())
            embedVar.set_image(url=summon["url"])

            # Aviso dos rolls
            pfp = username.avatar_url
            if user_data[f"{ctx.author.id}"]["rolls"] == 0:
              embedVar.set_footer(text=f'⚠️  ACABARAM OS ROLLS  ⚠️ · Pertence a {username}',icon_url=pfp)
            elif user_data[f"{ctx.author.id}"]["rolls"] <= 3:
              embedVar.set_footer(text=f'⚠️  {user_data[f"{ctx.author.id}"]["rolls"]} ROLLS RESTANTES  ⚠️ · Pertence a {username}',icon_url=pfp)
            else:
              embedVar.set_footer(text=f'Pertence a {username}',icon_url=pfp)

            msg = await ctx.channel.send(embed=embedVar)
            await msg.add_reaction('💸')
                
            # Criação da reação + verificação 
            def check(reaction, user):
              return str(reaction.emoji) == str(reaction.emoji) and user != client.user and msg.id == reaction.message.id and user_data[f"{user.id}"]["granacd"] > 0

            try:
              reaction, user = await client.wait_for('reaction_add', timeout=60, check=check)
            except:
              pass
              #await ctx.send(f'Você não pode reagir a 💸. {msg_claim_reset} (**$bal**)')
            else:
              granarandom = random.randint(5,100)
              user_data[f"{user.id}"]["granacd"] -= 1
              user_data[f"{user.id}"]["grana"] += granarandom
              await ctx.send(f':basketball:  **{user.name}** cobrou **{granarandom}** 💸 de **{summon["nome"]}**!  :basketball:')

        # Não tem mais rolls
        else:
          await ctx.send(f'**{ctx.author.name}**, os rolls são limitado a **10** usos por hora. {msg_rolls_reset}')
        
        with open("users.json", "w+") as fp:
          json.dump(user_data, fp, indent=4)

        with open("roster.json", "w+") as fp:
          json.dump(summon_data, fp, indent=4)

####################################################################################################
async def get_username_by_id(id):
  return await client.fetch_user(id)


##### REGISTRAR #####
def registrar(ctx):
  if os.path.isfile("users.json"):
    with open("users.json", "r") as fp:
        user_data = json.load(fp)
    try:
      if str(ctx.author.id) not in user_data:
        user_data[f"{ctx.author.id}"] = {"nome": str(ctx.author),"rolls": 10,"claim": 1,"grana": 0,"granacd": 1,"dk":1}
  
    except AttributeError:
      if str(ctx) not in user_data:
        user_data[f"{ctx}"] = {"nome": str(get_username_by_id(ctx)),"rolls": 10,"claim": 1,"grana": 0,"granacd": 1,"dk":1}
    
    with open("users.json", "w+") as fp:
      json.dump(user_data, fp, sort_keys=True, indent=4)

##### MARRY UP #####
@client.command()
async def mu(ctx):
    registrar(ctx)
    with open("users.json", "r") as fp:
        user_data = json.load(fp)
        user_claim = user_data[f"{ctx.author.id}"]["claim"]

    if user_claim:
        await ctx.send(f"**{ctx.author.name}**, você pode contratar agora mesmo! {msg_claim_reset}")
    else:
        await ctx.send(f"**{ctx.author.name}** calma aí, falta um tempo antes que você possa contratar novamente! {msg_claim_reset}")

##### VIZUALIZAR GERENTE #####
@client.command()
async def mma(ctx, user: discord.User = False):
    registrar(ctx)
    if user == client.user:
      await ctx.send(f"Acho que você esqueceu de marcar outra pesssoa.....")
    
    else:
      if not user:
        user_id = ctx.author.id
      else:
        user_id = user.id

      user = await client.fetch_user(user_id)
      pfp = user.avatar_url
    
      with open("roster.json", "r") as fp:
        summon_data = json.load(fp)
    
      desc = ''
      posicao = 1
      for key in summon_data:
        if summon_data[key]['gerente'] == user_id:
          desc += f"{posicao}° {summon_data[key]['nome']} \n"
          posicao += 1
      embedVar = discord.Embed(title=f'Contratos de {(await client.fetch_user(user_id)).name}', description=desc, color = discord.Colour.random())

      if posicao == 1:
        embedVar = discord.Embed(title=f'Contratos de {(await client.fetch_user(user_id)).name}', description='Oops, parece que você não contratou nenhum jogador!', color = discord.Colour.random(),thumbail = pfp)
      embedVar.set_thumbnail(url=pfp)
      
      await ctx.channel.send(embed=embedVar)

##### VIZUALIZAR JOGADOR #####
@client.command()
async def im(ctx, *nome_digitado:str ):
    if os.path.isfile("roster.json"):
        with open("roster.json", "r") as fp:
            summon_data = json.load(fp)
        nome_digitado = (' '.join(nome_digitado)).lower()

        for key in summon_data:
            nome_do_jogador = summon_data[key]['nome'].lower()

            if nome_digitado in nome_do_jogador:
                embedVar = discord.Embed(title=summon_data[key]["nome"], description=f'_{summon_data[key]["time"]}_\n_Camisa #{summon_data[key]["camisa"]}_', color = discord.Colour.random())
                embedVar.set_image(url=summon_data[key]["url"])
            
                if summon_data[key]['gerente'] != "sem_gerente":
                    user = await client.fetch_user(summon_data[key]["gerente"])
                    pfp = user.avatar_url
                    embedVar.set_footer(text=f'Pertence a {user.name}',icon_url=pfp)
                
                msg = await ctx.channel.send(embed=embedVar)
                break

##### TRADE #####
@client.command()
async def trade(ctx, user: discord.User = False):
    registrar(ctx)

    if not user or user.id == ctx.author.id or user == client.user:
      await ctx.send(f"Acho que você esqueceu de marcar outra pesssoa.....")

    else:
      player_1_id = ctx.author.id
      player_2_id = user.id
      
    with open("roster.json", "r") as fp:
      summon_data = json.load(fp)
    
      contador_p1 = 0
      contador_p2 = 0
      
      for key in summon_data:
        if summon_data[key]['gerente'] == player_1_id:
          contador_p1 += 1
        elif summon_data[key]['gerente'] == player_1_id:
          contador_p2 += 1
      
      if contador_p1 and contador_p2:
        await ctx.send(f"Estão faltando alguns contratos aí...")
      
      else:
        await ctx.send(f"**{(await client.fetch_user(player_2_id)).name}**, você concorda com essa troca? (S/N)")

        def check(m: discord.Message):
          return m.author.id == player_2_id and m.channel.id == ctx.channel.id and str(m.content).lower() in ['s','y','sim','yes']
        try:
          msg = await client.wait_for('message', check = check, timeout = 60.0)

        except: 
          await ctx.send(f"O tempo da negociação acabou!")
          return
      
        # JOGADOR 1
        else:
          await ctx.send(f"**{ctx.author.name}**, escreva o nome do jogador que você deseja trocar:")
          def check(m: discord.Message):
            if m.author.id == player_1_id and m.channel.id == ctx.channel.id:
              if os.path.isfile("roster.json"):
                with open("roster.json", "r") as fp:
                  summon_data = json.load(fp)
                
                nome_digitado = m.content.lower()
                
                for key in summon_data:
                  nome_do_jogador = summon_data[key]['nome'].lower()

                  if nome_digitado in nome_do_jogador:
                    if summon_data[key]['gerente'] == player_1_id:
                      global key_p1
                      key_p1 = key
                      return True
          try:
            msg = await client.wait_for('message', check = check, timeout = 60.0)

          except: 
            await ctx.send(f"O tempo da negociação acabou!")
            return
          
          else:
            await ctx.send(f"**{(await client.fetch_user(player_2_id)).name}**, escreva o nome do jogador que você deseja trocar:")
          
            def check(m: discord.Message):
              if m.author.id == player_2_id and m.channel.id == ctx.channel.id:
                if os.path.isfile("roster.json"):
                  with open("roster.json", "r") as fp:
                    summon_data = json.load(fp)
        
                  nome_digitado = m.content.lower()

                  for key in summon_data:
                    nome_do_jogador = summon_data[key]['nome'].lower()

                    if nome_digitado in nome_do_jogador:
                      if summon_data[key]['gerente'] == player_2_id:
                        global key_p2
                        key_p2 = key
                        return True
            try:
              msg = await client.wait_for('message', check = check, timeout = 60.0)

            except: 
              await ctx.send(f"O tempo da negociação acabou!")
              return
              
            else:
                with open("roster.json", "w+") as fp:
                  summon_data[key_p1]["gerente"],summon_data[key_p2]["gerente"] = summon_data[key_p2]["gerente"], summon_data[key_p1]["gerente"]
                  json.dump(summon_data, fp, indent=4)
                await ctx.send(f"Negociação concluída com sucesso.")

##### GRANA #####
@client.command()
async def bal(ctx):
    registrar(ctx)

    with open("users.json", "r") as fp:
        user_data = json.load(fp)
        user_grana = user_data[f"{ctx.author.id}"]["grana"]
    await ctx.send(f"Você possuí **{user_grana}** 💸 de grana.\n(Use **$loja** para gastar sua grana)  ")

##### RESET CLAIM #####
def reset_claim():
  threading.Timer(60, reset_claim).start()
  horario_atual = datetime.now()

  hora = int(horario_atual.strftime("%H"))
  minutos = int(horario_atual.strftime("%M"))
  
  global reset
  try:
    if hora == reset:
      if os.path.isfile("users.json"):
        reset += 3
        if reset == 24:
          reset = 0

        with open("users.json", "r") as fp:
          user_data = json.load(fp)
        for key in user_data:
          user_data[f"{key}"]["claim"] = 1
          user_data[f"{key}"]["granacd"] = 1
          user_data[f"{key}"]["dk"] = 1
        with open("users.json", "w+") as fp:
          json.dump(user_data, fp, indent=4)

  except:
    if hora < 3:
      reset = 3
    elif hora < 6:
      reset = 6
    elif hora < 9:
      reset = 9
    elif hora < 12:
      reset = 12
    elif hora < 15:
      reset = 15
    elif hora < 18:
      reset = 18
    elif hora < 21:
      reset = 21
    elif hora >= 21:
      reset = 0
  
  reset_claim_conv = datetime.strptime(f'{reset}:00', '%H:%M') - datetime.strptime(f'{hora}:{minutos}', '%H:%M')
  reset_claim_conv = (int(reset_claim_conv.seconds / 60)) 

  if hora == 23:
    hora_temp = 0
  else:
    hora_temp = hora + 1

  reset_rolls_conv = datetime.strptime(f'{hora_temp}:00', '%H:%M') - datetime.strptime(f'{hora}:{minutos}', '%H:%M')
  reset_rolls_conv = (int(reset_rolls_conv.seconds / 60)) 

  global msg_claim_reset
  if reset_claim_conv > 60:
    msg_claim_reset = f'A próxima reinicialização é em **{round(reset_claim_conv/60)}** hora(s).'
  else:
    msg_claim_reset = f'A próxima reinicialização é em **{reset_claim_conv}** minutos(s).'
  
  global msg_rolls_reset
  msg_rolls_reset = f'**{reset_rolls_conv}** minuto(s) até próximo reset.'

  if minutos == 0:
      if os.path.isfile("users.json"):
          with open("users.json", "r") as fp:
              user_data = json.load(fp)
          for key in user_data:
            user_data[f"{key}"]["rolls"] = 10
          with open("users.json", "w+") as fp:
            json.dump(user_data, fp, indent=4)
reset_claim()

##### DAILY GRANA #####
@client.command()
async def dk(ctx):
  registrar(ctx)
  with open("users.json", "r") as fp:
      user_data = json.load(fp)
  if user_data[f'{ctx.author.id}']['dk']:
    chance = random.randint(1,100)
    if chance >= 75:
      granarandom = random.randint(100,250)
    else:
      granarandom = random.randint(25,75)    
  
    user_data[f'{ctx.author.id}']["grana"] += granarandom
    user_data[f'{ctx.author.id}']["dk"] = 0
    with open("users.json", "w+") as fp:
          json.dump(user_data, fp, indent=4)
  
    with open("roster.json", "r") as fp:
          summon_data = json.load(fp)
        
          random_index = str(random.randint(1,len(summon_data)))
        
          nome_aleatorio = summon_data[random_index]["nome"]
          time_aleatorio = summon_data[random_index]["time"]
    msg_dm = [
f'Algum fã do {nome_aleatorio} deu **+{granarandom}** 💸 para você.',
f'Você recolheu **+{granarandom}** 💸 de seus jogadores.',
f'Os tocedores do {time_aleatorio} doaram **+{granarandom}** 💸 para você perder o próximo jogo.',
f'Você apostou no {time_aleatorio} e ganhou **+{granarandom}** 💸.',
f'Você se envolveu em uma polêmica com {nome_aleatorio}. **+{granarandom}** 💸.',
f'Você ganhou uma viagem para NBA House e **+{granarandom}** 💸.',
f'O treinador do {time_aleatorio} pediu algumas dicas para você. **+{granarandom}** 💸.'  ]
    await ctx.send(random.choice(msg_dm))
  else:
    msg_dm = f'Você já resgatou a sua grana. {msg_claim_reset}'
    await ctx.send(msg_dm)

#### PAGAR ####
@client.command()
async def pix(ctx, user: discord.User = False, grana = 0):
    registrar(ctx)
    with open("users.json", "r") as fp:
        user_data = json.load(fp)

    try:
      if user != client.user:
        grana = int(grana)  
        if user_data[f'{ctx.author.id}']["grana"] >= grana:
          user_data[f'{ctx.author.id}']["grana"] -= grana
          user_data[f'{user.id}']["grana"] += grana
          with open("users.json", "w+") as fp:
            json.dump(user_data, fp, indent=4)
          await ctx.send(f"**{user.name}** recebeu **+{grana}** 💸 de **{ctx.author.name}**!")
        else:
          await ctx.send(f"Você não tem grana sucifiente para essa transação!")
    except:
      await ctx.send(f"Acho que você esqueceu de alguma coisa....(Sintaxe: $pix @Alguém <número de grana para dar)")

##### SAIR #####
@client.command() #comando para desligar o bot pelo discord
async def sair(ctx):
    
    if ctx.author.id == 263067822635220992:
        await ctx.channel.send(':zzz:')
        exit()
    else:
        await ctx.channel.send(f'**{ctx.author.name}** quem é você?')

client.run(TOKEN)
