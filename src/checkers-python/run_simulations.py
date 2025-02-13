from Tools.Sample_AIs.Random_AI.GameLogic import GameLogic

def runSimulations(num_games):
    player1_wins = 0
    ties = 0

    for i in range(num_games):
        game = GameLogic(7, 7, 2, 'l', debug=False)
        result = game.Run(mode='l', ai_path_1='src/checkers-python/main.py', ai_path_2='Tools/Sample_AIs/Random_AI/main.py', time=1200)

        if result == 1:
            player1_wins += 1
        elif result == -1:
            ties += 1
        print(i)
    
    print(player1_wins, ties, num_games)
    return (player1_wins + ties) / num_games * 100
        


