import { useMemo, useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import {
  Camera,
  Thermometer,
  Droplet,
  Sprout,
  Activity,
  Wifi,
} from "lucide-react";

export function Dashboard() {
  const [isPaused, setIsPaused] = useState(false);
  const streamUrl = useMemo(
    () => import.meta.env.VITE_STREAM_URL ?? "http://localhost:8000/video_feed",
    []
  );

  const telemetryData = [
    {
      label: "Temperature",
      value: "--",
      unit: "°C",
      icon: Thermometer,
    },
    {
      label: "Humidity",
      value: "--",
      unit: "%",
      icon: Droplet,
    },
    {
      label: "Soil Moisture",
      value: "--",
      unit: "%",
      icon: Sprout,
    },
    {
      label: "Water Level",
      value: "--",
      unit: "%",
      icon: Droplet,
    },
    {
      label: "Signal Strength",
      value: "--",
      unit: "%",
      icon: Wifi,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Live Camera Feed */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Camera className="w-5 h-5 text-[#4CAF50]" />
            <h3>Live Camera Feed</h3>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsPaused(!isPaused)}
            >
              {isPaused ? "Resume Feed" : "Pause Feed"}
            </Button>
            <Button variant="outline" size="sm">
              Capture Image
            </Button>
          </div>
        </div>
        <div className="relative aspect-video bg-gradient-to-br from-[#4CAF50]/10 to-[#795548]/10 rounded-lg overflow-hidden flex items-center justify-center">
          <img
            src={streamUrl}
            alt="Live rover feed"
            className={`w-full h-full object-cover ${isPaused ? "opacity-50" : ""}`}
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.opacity = "0.3";
            }}
          />
          {isPaused && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Badge variant="secondary" className="px-4 py-2">
                Feed Paused
              </Badge>
            </div>
          )}
        </div>
      </Card>

      {/* Rover Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-2">
              Rover Status
            </p>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-400 rounded-full" />
              <span className="text-muted-foreground">
                Idle
              </span>
            </div>
          </div>
          <Activity className="w-8 h-8 text-muted-foreground" />
        </div>
      </Card>

      {/* Telemetry Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {telemetryData.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label} className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  {item.label}
                </p>
              </div>
              <p className="text-2xl mb-2">
                {item.value}
                <span className="text-sm text-muted-foreground ml-1">
                  {item.unit}
                </span>
              </p>
              <Progress value={0} className="h-2" />
            </Card>
          );
        })}
      </div>
    </div>
  );
}
