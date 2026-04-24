summary_path = fullfile('results', 'summary_metrics.csv');

if ~isfile(summary_path)
    error('Missing summary file: %s. Run Python simulation first.', summary_path);
end

T = readtable(summary_path);

scenarios = {'low', 'medium', 'high'};
mean_wait = zeros(1, numel(scenarios));
mean_throughput = zeros(1, numel(scenarios));
mean_util = zeros(1, numel(scenarios));

for i = 1:numel(scenarios)
    mask = strcmp(T.scenario, scenarios{i});
    mean_wait(i) = mean(T.avg_passenger_wait(mask));
    mean_throughput(i) = mean(T.throughput(mask));
    mean_util(i) = mean(T.utilization(mask));
end

x = 1:numel(scenarios);

figure('Color', 'w');
plot(x, mean_wait, '-o', 'LineWidth', 2);
xticks(x);
xticklabels(scenarios);
xlabel('Demand scenario');
ylabel('Average passenger wait');
title('Waiting Time vs Demand');
grid on;
saveas(gcf, fullfile('results', 'waiting_vs_demand.png'));

figure('Color', 'w');
plot(x, mean_throughput, '-o', 'LineWidth', 2);
xticks(x);
xticklabels(scenarios);
xlabel('Demand scenario');
ylabel('Throughput (completed requests per second)');
title('Throughput vs Demand');
grid on;
saveas(gcf, fullfile('results', 'throughput_vs_demand.png'));

figure('Color', 'w');
plot(x, mean_util, '-o', 'LineWidth', 2);
xticks(x);
xticklabels(scenarios);
xlabel('Demand scenario');
ylabel('Driver utilization');
title('Utilization vs Demand');
grid on;
saveas(gcf, fullfile('results', 'utilization_vs_demand.png'));

disp('Plots generated in results folder.');
