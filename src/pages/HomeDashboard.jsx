import ProviderConfig from "../components/ProviderConfig";
import AddChallan from "../components/AddChallan";
import CsvUpload from "../components/CsvUpload";
import ChallanList from "../components/ChallanList";

export default function HomeDashboard() {
  return (
    <>
      {/* PROVIDER CONFIG */}
      <ProviderConfig />

      {/* MANUAL CHALLAN ENTRY */}
      <AddChallan />

      {/* CSV UPLOAD */}
      <CsvUpload />

      {/* CHALLAN TABLE */}
      <ChallanList />
    </>
  );
}
