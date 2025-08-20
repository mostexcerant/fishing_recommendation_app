import React, { useState } from "react";
import { StyleSheet, Text, View, TextInput, Button, ScrollView } from "react-native";

export default function App() {
  const [species, setSpecies] = useState("");
  const [stateName, setStateName] = useState("");
  const [result, setResult] = useState(null);

  const planTrip = async () => {
    try {
      const res = await fetch("https://your-backend.example.com/plan_trip", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ species, state: stateName })
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setResult({ error: e.message });
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Fishing Trip Planner</Text>
      <TextInput placeholder="Species" style={styles.input} value={species} onChangeText={setSpecies} />
      <TextInput placeholder="State" style={styles.input} value={stateName} onChangeText={setStateName} />
      <Button title="Plan Trip" onPress={planTrip} />
      <ScrollView style={{marginTop:12}}>
        <Text>{JSON.stringify(result, null, 2)}</Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, padding:20, marginTop:40 },
  title: { fontSize:20, marginBottom:12 },
  input: { borderWidth:1, borderColor:"#ccc", padding:8, marginBottom:8 }
});
