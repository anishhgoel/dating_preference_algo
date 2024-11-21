# Gale Shapely Algorithm:

- Group A (Proposers) - They want to propose
- Group B (Acceptors) - They want to accept or reject the proposal

Each person in Group A has list of preffered partners in Group B, and vice versa. 
- Goal : To form stable pairs, where no one in pair would prefer someone else over their current partners.

### Possible Problems in the algorithm:

- Someone in Group A prefers someone in Group B more than their current partner.
- Someone in Group B prefers someone in Group A more than their current partner.

### How Gale Shapely comes into action

- All people are matched
- No one wants to "break up" their pair for someone else

## Working of Algorithm

### Everyone starts free:
- All members of Group A are single.
- All members of Group B are single.

### Proposal begins:
- Each member in Group A proposes to their favorite choice (top preference) in Group B.
- If a member in Group B is already paired, they compare the new proposer to their current partner.
    - If they prefer the new proposer, they break up with their current partner and accept the new one.
    - If they prefer their current partner, they reject the proposal.

### Repeat until everyone is paired:

- Members of Group A who were rejected move on to propose to the next person in their preference list.
- This continues until everyone in Group A is matched.

## Key Points:
- No one proposes to the same person twice.
- Members of Group B always hold on to the best option they've seen so far.
- At the end, all pairs are stable.

 
 #### The proposing group has the advantage:

 1. The proposers (Group A) have the freedom to choose whom to propose to based on their preferences.
 2. The acceptors (Group B) can only react to proposals and must choose the best proposal so far. They have no control over who proposes to them.
3. Over time, proposers can “trade up” if they are rejected, always moving down their preference list, ensuring they never settle for someone lower than necessary.
4. Acceptors always hold onto their best offer available at the time, but they don’t get to see all possible offers at once. This means they might miss out on a “better” match that comes later because they’re already engaged.





#Things to work on:

- when a user wants to change location, we want to make sure that the combination of city, state, country is valid