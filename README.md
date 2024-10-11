WIP, not release ready. If you've stumbled across this, do not use yet. It will only mess up your project.

# NoComply BG3 Dialogue Finder

## Overview
 - Search Baldur’s Gate 3’s audio files by dialogue, character and filename. Database contains all .wem files stored in english.pak and SharedSounds.pak.
 - Ability to for the community to edit database entries to improve accuracy.

## Installation
 - Online web app with edit feature <a href="https://bg3dialoguefinder.xyz/">here</a> (recommended).
 - Offline via Github: Just download, run app.py and copy the link provided by your terminal into your browser. I'll update the repo with the live database every week or so.

## Use Cases

 - For modding dialogue audio in Baldur’s Gate 3.

## More Information & Usage

### Database Creation and Accuracy
 
  Localization are referenced in english.loca along with the relevant subtitle. Accuracy for these should be 100%. There are some .wems in the Localization directory that are not used in english.loca. These may be cut content. At some point I will run these through Whisper and add them to the database. Character names were scraped from Pandora’s list of Voice UUIDs. 

  SharedSounds files were harder:

  • There are no subtitles for these so I ran the whole directory through OpenAI Whisper Large model (compute time: 134 hours, my CPU is screaming at me). Accuracy for any of these files that contain dialogue should be 90-100%. 

  • SharedSounds character names are currently only added for the files listed in TealRabbit19’s Point-Click Dialogue Files Database. While endlessly useful, by the creator's own admission this database is not 100% accurate. These character names can be submitted for revision in the search results. 

  • Whisper will likely have printed garbled nonsense/bizarre sentences for any files in SharedSounds that don’t contain dialogue. If you find any of these feel free to submit for revision.


### Usage Examples

You can use both search boxes to execute more complex queries, e.g. searching ‘Astarion’ in Characters and ‘tadpole’ in Dialogue will return all instances of Astarion saying tadpole. These work together as ‘and’ functions, not ‘or’ functions, i.e. searching for 'Astarion' in Characters and 'Gale' in Characters would return nothing as there is no character with both of those names. 

'Type' refers to the type of dialogue. All Localization files have the type: 
  ```
  Localization (Subtitled)
  ```

For the types in SharedSounds, I have referred to the resource identifiers in /[PAK]_Vocals/_merged.lsf. They are as follows:
  ```
  Action_Attack
  Action_Attack Stealth
  Action_BuffTarget
  Action_BuffTarget Negative
  Action_BuffTarget Postive
  Action_BuffTarget Romance
  Action_BuffTarget Stealth
  Action_BuffTarget Stealth Negative
  Action_BuffTarget Stealth Positive
  Action BuffTarget Stealth Romance
  Action_Dip
  Action_Dip Combat
  Action_Dip Stealth
  Action_HealTarget
  Action_HealTarget Negative
  Action_HealTarget Positive
  Action_HealTarget Romance
  Action_HealTarget Stealth
  Action_HealTarget Stealth Negative
  Action_HealTarget Stealth Positive
  Action_HealTarget Stealth Romance
  Action_HelpGeneric
  Action_HelpGeneric Negative
  Action_HelpGeneric Positive
  Action_HelpGeneric Romance
  Action_HelpGeneric Stealth
  Action_HelpGeneric Stealth Negative
  Action_HelpGeneric Stealth Positive
  Action_HelpGeneric Stealth Romance
  Action_HelpImmobilized
  Action_HelpImmobilized Negative
  Action_HelpImmobilized Positive
  Action_HelpImmobilized Romance
  Action_HelpImmobilized Stealth
  Action_HelpImmobilized Stealth Negative
  Action_HelpImmobilized Stealth Positive
  Action_HelpImmobilized Stealth Romance
  Action_InteractWith
  Action_InteractWith Combat
  Action_InteractWith Stealth
  Action_ItemPickup
  Action_ItemPickup Stealth
  Action_OpenContainer
  Action_OpenContainer Combat
  Action_OpenContainer Stealth
  Action_OpenLock
  Action_OpenLock Combat
  Action_OpenLock Stealth
  Action_PickPocket
  Action_SpeakTo
  Action_SpeakTo Negative
  Action_SpeakTo Positive
  Action_SpeakTo Stealth
  Action_SpeakTo Stealth Negative
  Action_SpeakTo Stealth Positive
  Action_Utility
  Action_Utility Combat
  Action_Utility Stealth
  ReptAction_HideSuccess
  ReptAction_MoveTo
  ReptAction_PickPocketSuccess
  ReptAction_PickPocketSuccess Combat
  ReptAction_PortraitClick
  ReptAction_PortraitClick Combat
  ReptAction_PortraitClick Stealth
  ReptAction_PortraitClickDowned
  ReptAction_PortraitClickSpam
  ReptAction_PortraitClickSpam Stealth
  ```
Sometimes these have character-specific modifiers appended such as `(Durge)` for dark urge-specific lines.

  
## Planned Features

 - Add audio file lengths. Could be useful for localization mods, as these are required to be the same length or shorter than the vanilla files in order to play correctly in-game without cutting off.

 - Add localizaton files missing from english.loca (likely cut content).


## Special Thanks

 - **Pandora (Nexus)**, for their list of Voice UUIDs. Invaluable.
 - **TealRabbit19 (Nexus)**, for their extraordinary labour of love in manually creating their Dialogue Files Database. Your patience astounds me.
 - **Larian Studios**, for their support of the modding community.


## Changelog
```
10/10/24 - V0.2b - Implemented revision system & download functionality. Minor GUI changes.
10/06/24 - V0.1b - Initial Version. Localization only, SharedSounds not yet implemented. Not for use.
```
