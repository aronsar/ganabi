# Copy over code from earlier version.
# Load the data if it already exists, otherwise create it

from utils import parse_args
from utils import dir_utils

@gin.configurable
class Dataset:
    def __init__(self, 
                 args, 
                 batch_size=1): 
        self.train_data = {} # gameplay data given to model
        self.validation_data = {} # data not given to model, from same agents as train
        self.test_data = {} # data from agents totally unseen to model
        self.batch_size = batch_size
        
    def read(self, raw_data)
        # split up raw_data into train, validation, and test
        test_agent = random.choice(list(self.all_data.keys()))

        for agent in raw_data:
            if agent == test_agent:
                continue
            split_idx = int(0.9 * len(raw_data[agent]))
            self.train_data[agent] = self.raw_data[agent][:split_idx]
            self.validation_data[agent] = self.raw_data[agent][split_idx:]
        
        self.test_data[test_agent] = raw_data[test_agent]


    def generator(self, batch_type='train'):
        if batch_type == 'train':
            data_bank = self.train_data
        elif batch_type == 'validation':
            data_bank = self.validation_data
        elif batch_type == 'test':
            data_bank = self.test_data
        
        # data_bank: [AgentName][num_games][0 = 
        #         obs_vec, 1 = act_vec][game_step][index into vec]
        agent = random.choice(data_bank.keys())
        adhoc_games = [random.choice(list(data_bank[agent])) 
                for _ in range(NUM_ADHOC_GAMES)]
        game_lengths = [len(game[0]) for game in adhoc_games]
        
        # adhoc_games: [-->[[obs_act_vec],[obs_act_vec],...]<--game1, 
        #               -->[[obs_act_vec],[obs_act_vec],...]<--game2...]
        adhoc_games = [[adhoc_games[i][0][l] + adhoc_games[i][1][l] 
                       for l in range(game_lengths[i])] 
                       for i in range(NUM_ADHOC_GAMES)]
        
        # assemble generated agent observations and target actions
        agent_obs, agent_act = [], []
        for i in range(NUM_AGENT_OBS):
            game = random.choice(list(data_bank[agent]))
            step_num = random.randint(0, len(game[0])-1)
            agent_obs.append(game[0][step_num])
            agent_act.append(game[1][step_num])
        
        # convert nested uneven list of adhoc games into padded numpy array
        np_adhoc_games = np.zeros(shape=(NUM_ADHOC_GAMES, MAX_GAME_LEN, OBS_ACT_VEC_LEN)) 
        game_lengths = np.array(game_lengths)
        for game_num, game_len in enumerate(game_lengths):
            np_adhoc_games[game_num, :game_lengths[game_num], :] = 
                    np.asarray(adhoc_games[game_num])
        
        agent_obs = np.array(agent_obs)
        agent_act = np.array(agent_act)
        
        #FIXME: needs to return same_act
        return ([np_adhoc_games, game_lengths, agent_obs], agent_act)

def main(args):
    data = Dataset(args) # gin configured
    datapath = dir_utils.resolve_datapath(args.datadir)
    
    try:
        raw_data = pickle.load(open(datapath, "rb"))

    except: IOError
        # call data creator script
        raw_data = pickle.load(open(datapath, "rb"))
    
    data.read(raw_data)

    return data


if __name__ == "__main__":
    args = parse_args.parse()
    main(args)
