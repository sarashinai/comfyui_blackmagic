import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { applyTextReplacements } from "../../scripts/utils.js";

function logWidget(w){
    // console.log(Object.keys(w));
    // 0: "linkedWidgets"
    // 1: "options"
    // 2: "marker"
    // 3: "label"
    // 4: "clicked"
    // 5: "name"
    // 6: "type"
    // 7: "value"
    // 8: "y"
    // 9: "last_y"
    // 10: "width"
    // 11: "disabled"
    // 12: "hidden"
    // 13: "advanced"
    // 14: "tooltip"
    // 15: "element"
    // 16: "callback"
    console.log("!!! WIDGET !!!");
    if (w.name !== undefined) console.log("\tName: " + w.name);
    if (w.label !== undefined) console.log("\tLabel: " + w.label);
    if (w.options !== undefined) console.log("\tOptions: %o", w.options);
    if (w.linkedWidgets !== undefined) console.log("\tLinked Widgets: %o", w.linkedWidgets);
    if (w.marker !== undefined) console.log("\tMarker: " + w.marker);
    if (w.clicked !== undefined) console.log("\tClicked: " + w.clicked);
    if (w.y !== undefined) console.log("\tY: " + w.y);
    if (w.last_y !== undefined) console.log("\tLasy Y: " + w.last_y);
    if (w.width !== undefined) console.log("\tWidth: " + w.width);
    if (w.type !== undefined) console.log("\tType: " + w.type);
    if (w.disabled !== undefined) console.log("\tDisabled: " + w.disabled);
    if (w.hidden !== undefined) console.log("\tHidden: " + w.hidden);
    if (w.advanced !== undefined) console.log("\tAdvanced: " + w.advanced);
    if (w.element !== undefined) console.log("\tElement: " + w.element);
    if (w.callback !== undefined) console.log("\tCallback: " + w.callback);
    if (w.display !== undefined) console.log("\tDisplay: " + w.display);
}

app.registerExtension({
    name: "comfyui-blackmagic.textformatter",

    async beforeRegisterNodeDef(nodeType, nodeData, app){
        if (nodeData.name === "TextFormatter"){
            const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
                      
            nodeType.prototype.onNodeCreated = function() {
                if (originalOnNodeCreated) originalOnNodeCreated.call(this);

                let containingNode = this;

                // console.log(containingNode);

                for (const [i, w] of containingNode.widgets.entries()) {
                    // console.log(w.name);
                   
                    switch (w.name){
                        case "formatText":
                            // console.log(w);
                            containingNode.formatTextElement = w.inputEl;
                            break;
                        case "formattedText":
                            // console.log(w);
                            // this.disabled = true;
                            containingNode.formattedTextElement = w.inputEl;
                            break;
                    }
                }

                // console.log(containingNode.formatTextElement);
                // console.log(containingNode.formattedTextElement);

                containingNode.formattedTextElement.setAttribute("readonly", "true");

                containingNode.formatTextElement.onchange = 
                containingNode.formatTextElement.onkeydown = 
                containingNode.formatTextElement.onpaste = 
                containingNode.formatTextElement.oninput = function(){
                    // console.log(containingNode.formatTextElement.value);

                    if (containingNode.formatTextElement.value.length != 0){
                        // console.log(containingNode.formatTextElement.value);
                        // console.log(applyTextReplacements(app, containingNode.formatTextElement.value));

                        containingNode.formattedTextElement.value = applyTextReplacements(app, containingNode.formatTextElement.value);
                    }
                }

                if (containingNode.formatTextElement.value.length != 0) containingNode.onchange();

                // this.addWidget(
                //     "button", 
                //     "Add LORA", 
                //     null, 
                //     () => { 
                //         let instructionsWidget = null;
                //         let lora = "";
                //         let lora_strength = "";
                //         let loader = "";
                //         let blocks = "";
                //         let clip_strength = "";
                        
                //         for (const [i, w] of this.widgets.entries()) {
                //             // console.log(w.name);
                           
                //             switch (w.name){
                //                 case "instructions":
                //                     instructionsWidget = w;
                //                     break;
                //                 case "lora":
                //                     lora = w.value;
                //                     break;
                //                 case "lora_strength":
                //                     lora_strength = w.value;
                //                     break;
                //                 case "loader":
                //                     loader = w.value;
                //                     break;
                //                 case "blocks":
                //                     blocks = w.value;
                //                     break;
                //                 case "clip_strength":
                //                     clip_strength = w.value;
                //                     break;
                //             }
                //         }

                //         let instructions = [];

                //         if (instructionsWidget.value != ""){
                //             instructions = instructionsWidget.value.split("\n");
                //         }

                //         let duplicateIndex = -1;

                //         if (instructions.length != 0){
                //             // console.log(instructions);

                //             for (let i = 0; i < instructions.length; i++){
                //                 if (instructions[i].length != 0){
                //                     if (instructions[i][0] == '#') continue; // Skip commented lines

                //                     // console.log(`${i}: ${instructions[i]}`);

                //                     let info = instructions[i].split(" | ");

                //                     // console.log(info);

                //                     if (info.length == 4){
                //                         if (info[0].length == 0){
                //                             alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. Missing LORA.`);

                //                             return;
                //                         }

                //                         if (info[0].search(".safetensors") == -1){
                //                             alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. LORA must be formatted as "FULLNAME.safetensors"`);

                //                             return;
                //                         }

                //                         if (info[1].length == 0){
                //                             alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. Missing LORA strength.`);

                //                             return;
                //                         }

                //                         // console.log(parseFloat(info[1]));

                //                         if (isNaN(parseFloat(info[1]))){
                //                             alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. LORA strength must be a float value.`);

                //                             return;
                //                         }

                //                         if (info[2].length == 0){
                //                             alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. Missing loader.`);

                //                             return;
                //                         }

                //                         switch (info[2]){
                //                             case "cgthree":
                //                                 if (isNaN(parseFloat(info[3]))){
                //                                     alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. CLIP strength must be a float value.`);
        
                //                                     return;
                //                                 }
                //                                 break;
                //                             case "facok":
                //                                 if (!block_types.includes(info[3])){
                //                                     alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. BLOCKS must be "all", "single_blocks", or "double_blocks".`);
                //                                 }
                //                                 break;
                //                             default:
                //                                 alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. Unrecognized loader ${info[2]}`);
                //                                 return;
                //                         }

                //                         if (info[0].localeCompare(lora) == 0) duplicateIndex = i;
                //                     } else {
                //                         alert(`Line ${i + 1}: "${instructions[i]}"\n\nTextLoraMultiloader formatting error. Make sure each line is formatted as:\n\nLORA.safetensors | LORA_STRENGTH | cgthree | CLIP_STRENGTH\n\nor\n\nLORA.safetensors | LORA_STRENGTH | facok | BLOCKS`);
                //                     }
                //                 }
                //             }
                //         }

                //         let finalString = "";

                //         if (loader == "facok") finalString = `${lora} | ${lora_strength} | ${loader} | ${blocks}`;
                //         else finalString = `${lora} | ${lora_strength} | ${loader} | ${clip_strength}`;

                //         if (duplicateIndex != -1){
                //             if (!confirm(`TextLoraMultiloader already has an entry for ${lora}. Click OK to replace it with the new settings or Cancel to stop.`)){
                //                 return;
                //             }

                //             instructions[duplicateIndex] = finalString;
                //         } else {
                //             instructions.push(finalString);
                //         }

                //         let result = "";

                //         for (let i = 0; i < instructions.length; i++){
                //             result += `${instructions[i]}`;

                //             if (i != instructions.length - 1) result += '\n';
                //         }

                //         instructionsWidget.value = result;
                //     }, {
                //         width: 150
                //     } 
                // );
            };
        }
    },
});