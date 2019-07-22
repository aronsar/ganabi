package com.fossgalaxy.games.fireworks.utils;

import com.fossgalaxy.games.fireworks.state.Card;
import com.fossgalaxy.games.fireworks.state.CardColour;
import com.fossgalaxy.games.fireworks.state.GameState;
import com.fossgalaxy.games.fireworks.state.Hand;
import org.slf4j.Logger;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Created by webpigeon on 11/10/16.
 */
public class DataParserUtils {
    /**
     * The number of players that were in this game
     */
    public final int kPlayers;
    public final int kColors;
    public final int kRanks;
    public final int kHandSize;
    public final int kBitsPerCard;
    public final int kMaxDeckSize;
    public final int kMaxInformationTokens;
    public final int kMaxLifeTokens;
    public final int kMoveTypeCounts;
    public int steps;
    public int current_player;

    // utility class - no instances required
    public DataParserUtils(int NumPlayer) {
        this.kPlayers = NumPlayer;
        this.kColors = 5;
        this.kRanks = 5;
        this.kHandSize = getHandSize();
        this.kBitsPerCard = this.kColors * this.kRanks;
        this.kMaxDeckSize = 50;
        this.kMaxInformationTokens = 8;
        this.kMaxLifeTokens = 3;
        this.kMoveTypeCounts = 4;
        this.steps = -1;
        this.current_player = 0;
    }

    public int getHandSize() {
        if (this.kPlayers < 4) {
            return 5;
        } else {
            return 4;
        }
    }

    public int getHandSectionLength() {
        return (this.kPlayers - 1) * this.kHandSize * this.kBitsPerCard + this.kPlayers;
    }

    public int getBoardSectionLength() {
        return this.kMaxDeckSize - this.kPlayers * this.kHandSize + this.kColors * this.kRanks
                + this.kMaxInformationTokens + this.kMaxLifeTokens;
    }

    public int getDiscardSectionLength() {
        return this.kMaxDeckSize;
    }

    public int getLastActionSectionLength() {
        return this.kPlayers + this.kMoveTypeCounts + this.kPlayers + this.kColors + this.kRanks + this.kHandSize
                + this.kHandSize + this.kBitsPerCard + 2;
    }

    public int getCardKnowledgeSectionLength() {
        return this.kPlayers * this.kHandSize * (this.kBitsPerCard + this.kColors + this.kRanks);
    }

    public int getObservationShape() {
        return getHandSectionLength() + getBoardSectionLength() + getDiscardSectionLength()
                + getLastActionSectionLength() + getCardKnowledgeSectionLength();
    }

    // TODO
    public void encodeHandSection(GameState state, int offset, int[] obs) {
        int start_offset = offset;
        // Encode all other player's hands cards
        for (int player = 0; player < this.kPlayers; player++) {
            // Skip current player's hand deck
            if (player == this.current_player) {
                continue;
            }

            Hand hand = state.getHand(player);
            for (int slot = 0; slot < this.kHandSize; slot++) {
                Card card = hand.getCard(slot);

                if (card != null) {
                    Integer card_rank = card.value;
                    CardColour card_color = card.colour;

                    obs[offset + CardIndex(card_color, card_rank, this.kRanks)] = 1;
                    System.out.printf("Slot %d, Player %d, Card Color %s %d, Card Rank %d, Card Index %d\n", slot,
                            player, card_color, ColorToIndex(card_color), card_rank,
                            CardIndex(card_color, card_rank, this.kRanks));
                    System.out.printf("Offset %d, Index: %d\n", offset,
                            offset + CardIndex(card_color, card_rank, this.kRanks));
                }
                offset += this.kBitsPerCard;
            }
        }

        // For each player, set a bit if their hand is missing a card.
        for (int player = 0; player < this.kPlayers; player++) {
            if (state.getHand(player).getSize() < this.kHandSize) {
                obs[offset + player] = 1;
            }
        }
        offset += this.kPlayers;
        assert (offset - start_offset == getHandSectionLength());
    }

    // TODO
    public void encodeBoardSection(GameState state, int offset, int[] obs) {

    }

    // TODO
    public void encodeDiscardSection(GameState state, int offset, int[] obs) {

    }

    // TODO
    public void encodeLastActionSection(GameState state, int offset, int[] obs) {

    }

    // TODO
    public void encodeCardKnowledgeSection(GameState state, int offset, int[] obs) {

    }

    public void initSteps() {
        this.steps += 1;
        this.current_player = this.steps % this.kPlayers;
        // Sanity Check
        assert (this.current_player >= 0 && this.current_player <= 4);
    }

    public void writeObservation(GameState state) {
        int offset = 0;
        // Vector<Integer> obs = new Vector<Integer>(getObservationShape());
        int[] obs = new int[getObservationShape()];
        Arrays.fill(obs, 42);
        initSteps();

        System.out.printf("Step %d, Player ID %d\n", this.steps, this.current_player);

        encodeHandSection(state, offset, obs);
        encodeBoardSection(state, offset, obs);
        encodeDiscardSection(state, offset, obs);
        encodeLastActionSection(state, offset, obs);
        encodeCardKnowledgeSection(state, offset, obs);
    }

    // Utilies starts here
    // color-major index
    // public static int CardIndex(int color, int rank, int num_ranks) {
    // return color * num_ranks + rank;
    // }

    public static int CardIndex(CardColour color, int rank, int num_ranks) {
        return ColorToIndex(color) * num_ranks + rank;
    }

    // Python: Red, Yellow, Green, White, Blue
    // Java: Red, Blue, Green, Oragne, White
    public static int ColorToIndex(CardColour color) {
        int res = -1;
        switch (color) {
        case RED:
            res = 0;
            break;
        case BLUE:
            res = 4;
            break;
        case GREEN:
            res = 2;
            break;
        case ORANGE:
            res = 1;
            break;
        case WHITE:
            res = 3;
            break;
        default:
            break;
        }
        assert (res != -1);
        return res;
    }
}