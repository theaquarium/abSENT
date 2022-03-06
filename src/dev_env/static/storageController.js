class StorageController {
    static dateNumToDate(dateStr) {
        const newDate = new Date(parseInt(dateStr));
        return isNaN(newDate) ? newDate : new Date();
    }

    static updatesToObject(updateList) {
        const list = [];
        updateList.forEach((update) => {
            list.push({
                id: update.id,
                body: update.body,
                user: update.user,
                date: update.date.date.getTime(),
            });
        });
        return list;
    }

    static conversationListToObject(conversationList) {
        const result = {};
        Object.keys(conversationList).forEach((key) => {
            result[key] = conversationList[key].toObject();
        });
        return result;
    }

    static objectToUpdates(updateList) {
        const result = [];
        updateList.forEach((update) => {
            result.push(new Update({
                id: update.id,
                uid: update.user.id,
                name: update.user.name,
                body: update.body,
                date: formatDate(dateNumToDate(update.date)),
            }));
        });
        return result;
    }

    static objectToConversations(convoList) {
        const result = {};
        Object.keys(convoList).forEach((number) => {
            const textList = convoList[number].texts.map((text) => {
                return new SMSText(text);
            });
            result[number] = new Conversation({
                number: number,
                texts: textList,
            })
        });
        return result;
    }

    static getFullStorageObject(loadedObject) {
        const result = {
            conversations: StorageController.conversationListToObject(loadedObject.conversations),
            southUpdateFeed: StorageController.updatesToObject(loadedObject.southUpdateFeed),
            northUpdateFeed: StorageController.updatesToObject(loadedObject.northUpdateFeed),
            frozenDate: loadedObject.frozenDate ? loadedObject.frozenDate.date.getTime().toString() : null,
        }
        return result;
    }

    load() {
        const result = {
            conversations: {},
            southUpdateFeed: [],
            northUpdateFeed: [],
            frozenDate: null,
        };
        const conversationsString = localStorage.getItem('conversations');
        if (converationString !== null) {
            try {
                const conversationsObj = JSON.parse(conversationsString);
                result.conversations = StorageController.objectToConversations(conversationsObj);
            } catch (e) {
                console.error('Error parsing conversations JSON', e);
            }
        }
        
        const southUpdatesString = localStorage.getItem('south-updates');
        if (southUpdatesString !== null) {
            try {
                const southObj = JSON.parse(southUpdatesString);
                result.southUpdateFeed = StorageController.objectToUpdates(southObj);
            } catch (e) {
                console.error('Error parsing South updates JSON', e);
            }
        }

        const northUpdatesString = localStorage.getItem('north-updates');
        if (northUpdatesString !== null) {
            try {
                const northObj = JSON.parse(northUpdatesString);
                result.northUpdateFeed = StorageController.objectToUpdates(northObj);
            } catch (e) {
                console.error('Error parsing North updates JSON', e);
            }
        }

        const frozenDateString = localStorage.getItem('frozen-date');
        if (northUpdatesString !== null) {
            try {
                const frozenDateParsed = StorageController.dateNumToDate(frozenDateString);
                result.northUpdateFeed = formatDate(frozenDateParsed);
            } catch (e) {
                console.error('Error parsing frozen date', e);
            }
        }

        return result;
    }

    saveConversations(conversations) {
        const conversationsString = JSON.stringify(StorageController.conversationListToObject(converations));
        localStorage.setItem('conversations', conversationsString);
    }

    saveSouthUpdates(updates) {
        const updatesString = JSON.stringify(StorageController.updatesToObject(updates));
        localStorage.setItem('south-updates', updatesString);
    }

    saveNorthUpdates(updates) {
        const updatesString = JSON.stringify(StorageController.updatesToObject(updates));
        localStorage.setItem('north-updates', updatesString);
    }

    saveFrozenDate(frozenDate) {
        const dateString = frozenDate.getTime().toString();
        localStorage.setItem('frozen-date', dateString);
    }

    clearConversations() {
        localStorage.removeItem('conversations');
    }

    clearSouthUpdates() {
        localStorage.removeItem('south-updates');
    }

    clearNorthUpdates() {
        localStorage.removeItem('north-updates');
    }

    clearFrozenDate() {
        localStorage.removeItem('frozen-date');
    }
}
