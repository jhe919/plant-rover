import { Card } from './ui/card';
import { BarChart3, Droplet, Activity, CheckCircle2, TrendingUp } from 'lucide-react';

export function Analytics() {
  const kpis = [
    { label: 'Water Saved', value: '0L', icon: Droplet, color: 'text-blue-500' },
    { label: 'Plants Treated', value: '0', icon: CheckCircle2, color: 'text-[#4CAF50]' },
    { label: 'Operation Hours', value: '0h', icon: Activity, color: 'text-purple-500' },
    { label: 'Efficiency Score', value: '0%', icon: TrendingUp, color: 'text-[#FFEB3B]' },
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Card key={kpi.label} className="p-6">
              <div className="flex items-start justify-between mb-3">
                <Icon className={`w-5 h-5 ${kpi.color}`} />
              </div>
              <p className="text-sm text-muted-foreground mb-1">{kpi.label}</p>
              <p className="text-2xl">{kpi.value}</p>
            </Card>
          );
        })}
      </div>

      {/* Empty State */}
      <Card className="p-12">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="w-20 h-20 rounded-full bg-[#4CAF50]/10 flex items-center justify-center mb-4">
            <BarChart3 className="w-10 h-10 text-[#4CAF50]/50" />
          </div>
          <h3 className="mb-2">No Analytics Data Available</h3>
          <p className="text-muted-foreground max-w-md">
            Charts and reports will be generated once the rover collects operational data from field monitoring activities.
          </p>
        </div>
      </Card>
    </div>
  );
}
