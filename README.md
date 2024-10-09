WIP, not release ready. If you've stumbled across this, do not use yet. It will only mess up your project.

<u>NoComply BG3 Dialogue Finder</u>


<u>Overview</u>

 - Search Baldur’s Gate 3’s audio files by dialogue, character and filename. Database contains all .wem files stored in english.pak and SharedSounds.pak.
 - Ability to edit some database entries to improve accuracy. 


<u>Use Cases</u>

 - For the creation of audio-based mods for Baldur’s Gate 3.


<u>How I Did This</u>
 
Localization files were easy as they are referenced in english.loca along with the relevant subtitle. Accuracy for these should be 100%. There are some .wems in the Localization directory that are not used in english.loca. These may be cut content. At some point I will run these through Whisper and add them to the database. Character names were scraped from Pandora’s list of Voice UUIDs. 

SharedSounds files were harder. 

• There are no subtitles for these so I ran the whole directory through OpenAI Whisper Large model (compute time: 134 hours, my CPU is screaming at me). Accuracy for any of these files that contain dialogue should be 90-100%. 
• SharadSounds character names are currently only added for the files listed in TealRabbit19’s Point-Click Dialogue Files Database (important to note that, while endlessly useful, by the creator's own admission this database is not 100% accurate. These character names can be submitted for revision in the search results). 
• Whisper will likely have printed garbled nonsense for any files in SharedSounds that don’t contain dialogue. If you find any of these feel free to remove it with the edit function. 


<u>Usage Example</u>

You can use both search boxes to execute more complex queries, e.g. searching ‘Astarion’ in Characters and ‘tadpole’ in Dialogue will return all instances of Astarion saying tadpole. These work together as ‘and’ functions, not ‘or’ functions, i.e. searching for 'Astarion' in Characters and 'Gale' in Characters would return nothing as there is no character with both of those names. 


<u>Planned Features</u>

 - Ability to download search results.


<u>Special Thanks</u>

 - Pandora (Nexus), for their list of Voice UUIDs. Invaluable.
 - TealRabbit19 (Nexus), for their extraordinary labour of love in manually creating their Dialogue Files Database. Your patience astounds me.
 - Larian Studios, for their support of the modding community.


<u>Changelog</u>

6/10/24 - V0.1b - Initial Version. Localization only, SharedSounds not yet implemented. Not for use. 
