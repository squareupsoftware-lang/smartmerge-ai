import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, CartesianGrid
} from "recharts";

export default function Dashboard({ data, theme }) {

  return (
    <div>
      <h2>Analytics</h2>

      {/* BAR */}
      <BarChart width={500} height={250} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="Sales Person" stroke={theme.text}/>
        <YAxis stroke={theme.text}/>
        <Tooltip />
        <Bar dataKey="Amount" fill={theme.chart}/>
      </BarChart>

      {/* LINE */}
      <LineChart width={500} height={250} data={data}>
        <XAxis dataKey="Sales Person" stroke={theme.text}/>
        <YAxis stroke={theme.text}/>
        <Tooltip />
        <Line type="monotone" dataKey="Amount" stroke={theme.chart}/>
      </LineChart>

    </div>
  );
}



const fetchData = async () => {
  const token = localStorage.getItem("token");

  const res = await fetch("http://127.0.0.1:8000/data", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  const data = await res.json();
  setData(data);
};

const [country, setCountry] = useState("All");

const filteredData = data.filter(d =>
  country === "All" ? true : d.Country === country
);