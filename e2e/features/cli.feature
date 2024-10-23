Feature: using CLI

    Scenario Outline: sync text, audio and translation
        Given <language> text
        And <translation> text
        And <language> audio
        When run the app
        Then we get a folder with sync map

        Examples: Languages
            | language | translation |
            | French   | English     |
            | French   | Ukrainian   |
            | English  | Ukrainian   |
