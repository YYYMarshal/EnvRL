from tqdm import tqdm
import numpy as np
import torch
import collections
import random
import matplotlib.pyplot as plt
from datetime import datetime


class ReplayBuffer:
    """ 经验回放池 """

    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)  # 队列,先进先出

    def add(self, state, action, reward, next_state, done):  # 将数据加入buffer
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):  # 从buffer中采样数据,数量为batch_size
        transitions = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*transitions)
        return np.array(state), action, reward, np.array(next_state), done

    def size(self):  # 目前buffer中数据的数量
        return len(self.buffer)


def moving_average(a, window_size):
    cumulative_sum = np.cumsum(np.insert(a, 0, 0))
    middle = (cumulative_sum[window_size:] - cumulative_sum[:-window_size]) / window_size
    r = np.arange(1, window_size - 1, 2)
    begin = np.cumsum(a[:window_size - 1])[::2] / r
    end = (np.cumsum(a[:-window_size:-1])[::2] / r)[::-1]
    return np.concatenate((begin, middle, end))


def plot(return_list: [], algorithm: str, env_name: str):
    episodes_list = list(range(len(return_list)))
    xlabel = "Episodes"
    ylabel = "Returns"
    title = f"{algorithm} on {env_name}"
    plt.plot(episodes_list, return_list)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

    mv_return = moving_average(return_list, 9)
    plt.plot(episodes_list, mv_return)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def train_on_policy_agent(env, agent, num_episodes):
    return_list = []
    for i in range(10):
        with tqdm(total=int(num_episodes / 10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes / 10)):
                episode_return = 0
                transition_dict = {'states': [], 'actions': [], 'next_states': [], 'rewards': [], 'dones': []}
                state = env.reset()
                done = False
                while not done:
                    action = agent.take_action(state)
                    next_state, reward, done, _ = env.step(action)
                    transition_dict['states'].append(state)
                    transition_dict['actions'].append(action)
                    transition_dict['rewards'].append(reward)
                    transition_dict['next_states'].append(next_state)
                    transition_dict['dones'].append(done)
                    state = next_state
                    episode_return += reward
                return_list.append(episode_return)
                agent.update(transition_dict)
                if (i_episode + 1) % 10 == 0:
                    pbar.set_postfix({'episode': '%d' % (num_episodes / 10 * i + i_episode + 1),
                                      'return': '%.3f' % np.mean(return_list[-10:])})
                pbar.update(1)
    return return_list


def train_off_policy_agent(env, agent, num_episodes, replay_buffer,
                            minimal_size, batch_size, is_render=False, interval=10):
    return_list = []
    # 每运行 num_episodes * (1/interval) 次打印一次信息、显示画面（可选）
    part = num_episodes / interval
    for i_episode in range(num_episodes):
        episode_return = 0
        state = env.reset()
        done = False
        while not done:
            if is_render and i_episode % part == 0:
                env.render()
            action = agent.take_action(state)
            next_state, reward, done, info = env.step(action)
            replay_buffer.add(state, action, reward, next_state, done)
            state = next_state
            episode_return += reward
            # 当buffer数据的数量超过一定值后,才进行Q网络训练
            if replay_buffer.size() > minimal_size:
                b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                transition_dict = {
                    'states': b_s,
                    'actions': b_a,
                    'rewards': b_r,
                    'next_states': b_ns,
                    'dones': b_d}
                agent.update(transition_dict)
        return_list.append(episode_return)
        if i_episode % part == 0:
            print(f"{i_episode}/{num_episodes}, episode_return = {episode_return}")
        env.close()

    print("---------------------")
    print(f"回报的平均值 = {np.mean(return_list)}")
    return return_list


def compute_advantage(gamma, lmbda, td_delta):
    td_delta = td_delta.detach().numpy()
    advantage_list = []
    advantage = 0.0
    for delta in td_delta[::-1]:
        advantage = gamma * lmbda * advantage + delta
        advantage_list.append(advantage)
    advantage_list.reverse()
    return torch.tensor(advantage_list, dtype=torch.float)


def get_current_time():
    """
    显示当前时间的时分秒格式
    """
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    print(f"当前时间：{formatted_time}")
    return current_time


def time_difference(start_time):
    """
    计算当前时间减去给定时间的时间差
    """
    current_time = get_current_time()
    time_diff = current_time - start_time
    print(f"用时：{time_diff}")
    return time_diff
