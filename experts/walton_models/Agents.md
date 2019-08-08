---
tags: Ganabi 
---
[TOC]

# Walton Agent README
In this post, you will learn about
- Setup the environment to run our code using *create_load_data.py*
- Setup the environment to modify and compile the original walton agent code in Java
- High level overview of our implementation pipeline and design choices
- Subtle but important difference among the Python and Java Hanabi environment 


## Quick Start
Check if you have Java 8 available on your machine. Be aware that newer version such as Java 11 or Java 12 will most likely not work. 
```bash
# Check Java Version
$ java -version

openjdk version "1.8.0_212"
OpenJDK Runtime Environment (build 1.8.0_212-8u212-b03-0ubuntu1.18.04.1-b03)
OpenJDK 64-Bit Server VM (build 25.212-b03, mixed mode)


# # Install OpenJDK 8 if not installed
$ sudo add-apt-repository ppa:openjdk-r/ppa
$ sudo apt-get update
$ sudo apt-get install openjdk-8-jdk


# Switch btw different Java version on Ubuntu
$ sudo update-alternatives --config java

There are 2 choices for the alternative java (providing /usr/bin/java).

  Selection    Path                                            Priority   Status
------------------------------------------------------------
  0            /usr/lib/jvm/java-11-openjdk-amd64/bin/java      1111      auto mode
  1            /usr/lib/jvm/java-11-openjdk-amd64/bin/java      1111      manual mode
* 2            /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java   1081      manual mode

Press <enter> to keep the current choice[*], or type selection number: 
```

 The following is a list of the avaible agents name recognized by our python script.
- Walton_Agent_Name
    - 'iggi'
    - 'outer'
    - 'legal_random'
    - 'vdb-paper'
    - 'flawed'
    - 'piers'`


To generate the data, run 
```bash
python create_load_data.py --agents_to_use=Walton_Agent_Name
```

## Details
### Pipeline OverView
- Call create_load_data.py
- Create csv data from walton.jar
- Parse csv data and feed into python hanabi environment to produce reliable vectorized observation and action encoding (Timothy's Method)
- Save the encoding into a pickle file and remove the csv data


### Java Environment
The original walton agent is written in Java. Instead of using the provided bash script to generate the data, the *create_walton_data.py* script will [invoke a subprocess](https://github.com/aronsar/ganabi/blob/82d5a51240640eae90b4734e05015c11b1e9c4b1/experts/create_walton_data.py#L38) that generates the data from the *walton.jar* file.


### Jar File
> A JAR (Java ARchive) is a package file format typically used to aggregate many Java class files and associated metadata and resources (text, images, etc.) into one file for distribution.[3] It is used to store classes of java created by the user in order to help the runnable and inference concepts embedded within the language.

We have compiled and included the jar file beforehand. Unless you modified the original Java code, you will need not to worry about recompiling the jar file. We recommend you not to modify anything under *experts/waltonmodels* but contact us if you need any help.



### CSV Format
- Game number
    - 0~(N-1)
- Deck size (Redundant, remove in the future)
    - 50 
- Action Type
    - PLAY, DICARD, REVEAL_COLOR, REVEAL_RANK
- Played Card Color
    - R,G,Y,B,W
    - X stands for unknown color
- Played Card Rank
    - 0~4
    - -1 stands for unknown rank
- Deck Cards
    - "%s%d", card color, card rank 

Example:
```csv
game number, deck size, action type, played card color, played card rank, deck cards ......
0,50,REVEAL_RANK,X,0,W3,G1,B1,G2,B2,G0,G3,B3,G1,B4,Y2,Y1,W1,R1,W2,G0,W3,B0,R3,R2,R0,W0,B2,Y3,Y0,W1,Y0,W4,B1,G2,G0,G4,W0,G3,Y4,B3,R0,B0,W0,R4,Y3,B0,Y1,R2,R1,R0,Y0,R3,W2,Y2
```

### Implemenation Choice 
Due to the implementaion differences between the Java and Python Hanabi environment, there doesn't seem to be a way to directly generate the observation encoding. Thus, we sacraficed a bit of overhead by running the games in both environment to exchange for correctness of the encoding. As for now, the java hanabi environment is used for only extracting the starting deck and action at each step. The starting deck is used for initializing the game, and the action is used to step through a game until it is over.

To record the starting deck cards and the actions at each step, we've created a DataParserUtils class that manages all corresponding functionality. When a game is initialized, the data parser will store a copy of all the starting deck cards. At each game step, the data parser will store the action that is chosen. The recorded data will be written to a csv file whenever a game is terminated. To ensure the data integrity, the data will only be written to the file only if no action violates the rules throughout the entire game. 



## Others
### Modify and Compile Java Code
This section will focus more on helping you to understand how to change the walton model code base if needed. Yet, we still recommend you to not do so unless you have a strong reason and a firm understanding of how to do so.

We use the original scipt *[run_experiment.sh](https://github.com/aronsar/ganabi/blob/merge_refactor/experts/walton_models/run_experiment.sh)* to compile the project. The script can only be run in a clean directory. In other word, you will have to commit all your changes before using this script. In addition, we are using **Maven**, a Java package manager, to build the project. Thus, installation of maven is also required 

```bash
# Check Maven
$ mvn --version

Apache Maven 3.6.0
Maven home: /usr/share/maven
Java version: 1.8.0_212, vendor: Oracle Corporation, runtime: /usr/lib/jvm/java-8-openjdk-amd64/jre
Default locale: en_US, platform encoding: UTF-8
OS name: "linux", version: "4.15.0-55-generic", arch: "amd64", family: "unix"


# Install Maven
$ sudo apt-get install maven


# Template of using run_experiement.sh to generate data
./run_experiment.sh agent_name agent_name player_number total_game_number seed_number


# Record 10 games for 2 iggi agent, init with seed = 1
$ ./run_experiment.sh iggi iggi 2 10 1
```

Directory layout.
```
tree . -L 2
├── results
│   ├── 37a910683d7d319e2f4a04bb4ce25aede6fc06c8
│   ├── 83915eae9a56fe91308308adeffdd019adc2e28a
│   ├── ...
│   └── runs.log
├── run_experiment.sh
├── src
│   ├── main
│   └── test
├── target
│   ├── fireworks-0.2.6-SNAPSHOT.jar
│   ├── fireworks-0.2.6-SNAPSHOT-jar-with-dependencies.jar
│   ├──  ...
└── walton.jar
```

Remember that the python script relies on walton.jar? In fact, you will have to update walton.jar manually to have the python script to take effect of your latest updates. To update walton.jar

```bash
# You can(should) create a script on your own
$ cp target/fireworks-0.2.6-SNAPSHOT-jar-with-dependencies.jar .
$ rm walton.jar
$ mv fireworks-0.2.6-SNAPSHOT-jar-with-dependencies.jar walton.jar
```

### Java Hanabi VS Python Hanabi
In the early section, we've mentioned that our approach creates some overhead. In fact, our initial approach was to convert the encoding in observation and action in Java directly and stored in a csv file. However due to the following differences between the Java and Python Hanabi environment, we found out the initial approach is infeasible.

#### Slot
Assume a two player game where each player has five cards in their hands. Suppose the current action is having player A to play the card at slot 1, and draws a "Y4" from the start deck

Player A's hand before insertion
| Slot 0 | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
| ------ | ------ | ------ | ------ | ------ |
| B0     | B1     | B2     | B3     | B4     |

Player A's hand after insertion "Y4" in Java
| Slot 0 | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
| ------ | ------ | ------ | ------ | ------ |
| B0     | Y4     | B2     | B3     | B4     |

Player A's hand after insertion "Y4" in Python
| Slot 0 | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
| ------ | ------ | ------ | ------ | ------ |
| B0     | B2     | B3     | B4     | Y4     |

In short, the Python Hanabi have a "shift" mechanism whenever a player perform either PLAY or DISCARD action, but the Java Hanabi simply replaces with the new card in the same direction. Such difference shouldn't be ignored and can cause the direct encoding translation to fail.

#### Start Deck
In Python Hanabi, all 50 cards are initialized as the starting deck, and then each player draws from the starting deck to set its starting hand. However, the Java Hanabi initialize the starting deck and each players' starting hand seperately. As a result, it is important to use the correct way to transform the correct start deck information as it is being used to initialized the Python Hanabi environment. 

Luckily, the translation is relatively straightfoward. The overall logic is having player 1s hand cards follow by player 2s' hand cards on so on. Here is an example


Player 1's hand
| Slot 0 | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
| ------ | ------ | ------ | ------ | ------ |
| B0     | B1     | B2     | B3     | B4     |

Player 1's hand
| Slot 0 | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
| ------ | ------ | ------ | ------ | ------ |
| Y0     | Y1     | Y2     | Y3     | Y4     |

```python
# Python start_deck in list
start_deck = [
    "B0", "B1", "B2", "B3", "B4", 
    "Y0", "Y1", "Y2", "Y3", "Y4",
    ...other actual start deck cards in order
] 

# Initialize the game with correct start_deck
obs = env.reset(start_deck)
```

## Agents
### Legal Random
Agent makes move at random from the set of legal actions available at any given time step.

### Van den Bergh Rule
Best rule-based agent. It models human play such that:
•	If certain enough that card is playable then play it.
•	If certain enough that card is useless then discard it.
•	Give a hint if possible.
•	Discard a card.
Order of Operations:
•	If lives > 1 Then Plays card that it most likely to be playable as long as it has probability greater than 0.6. Else Play card that is guaranteed to be playable.
•	Discard a card that it most likely to be useless as long as probability is 1.
•	Tells next player with a useful card (either rank or suit known) the remaining unknown suit or rank of the card.
•	Tells next player with a useless card (either rank or suit known) the remaining unknown suit or rank of the card.
•	Tells whatever reveals the most information either in total or new.
•	Discard a card that it most likely to be useless.

### Flawed
Designed to be intelligent but with some flaws. Understanding the agent is the key to playing with it as other agents can give it information it needs to prevent exposing its flaws.
Order of Operations:
•	Play card that is guaranteed to be playable.
•	Plays card that it most likely to be playable as long as it is at least as probable as the threshold. Threshold is part of [0,1]
•	Tells the next player a random fact about any card in their hand.
•	Discard card that is not playable at the end of the turn.
•	Discard card that has been held in the hand for longest.
•	Randomly discards a card from their hand.

### Outer
Stores memory of its own hand, and knowledge of what other agents have been told already.
Order of Operations:
•	Play card that is guaranteed to be playable.
•	Discard card that is not playable at the end of the turn.
•	Tells next player an unknown fact about any playable card in their hand.
•	Tells next player an unknown fact about any card in their hand.
•	Randomly discards a card from their hand.

### IGGI 
Plays in way to ensure no loss of life. If discard is necessary, then the discarded card is chosen such that it is the oldest card in the agent’s hand. This makes the agent more predictable.
Order of Operations:
•	Plays card that is exactly known and is playable.
•	Play card that is guaranteed to be playable.
•	Tells next player with a useful card (either rank or suit known) the remaining unknown suit or rank of the card.
•	Discard card that is not playable at the end of the turn.
•	Discard card that has been held in the hand for longest.

### Piers
Plays according to intelligent tell rules which are designed to maximize score.
Intelligent Tell Rules:
•	If lives > 1 and deck has cards left, Then Plays card that it most likely to be playable as long as it has probability greater than 0.0.
•	Play card that is guaranteed to be playable
•	If lives > 1 Then Plays card that it most likely to be playable as long as it has probability greater than 0.6.
•	Tells next player with a useful card (either rank or suit known) the remaining unknown suit or rank of the card.
•	If information < 4 Then Tell next player with an unknown dispensable card information needed to identify the card is dispensable (Single piece of information makes it identifiable as dispensable).
•	Discard card that is not playable at the end of the turn.
•	Discard card that has been held in the hand for longest.
•	Tells the next player a random fact about any card in their hand.
•	Randomly discards a card from their hand.
